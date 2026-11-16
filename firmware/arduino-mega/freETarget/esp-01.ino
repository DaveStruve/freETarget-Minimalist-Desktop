/*----------------------------------------------------------------
 *
 * esp01.ino
 *
 * WiFi Driver for esp01
 * 
 *-----------------------------------------------------------------
 *
 * Refer to the command set which can be found at 
 * 
 * https://www.espressif.com/sites/default/files/documentation/4a-esp8266_at_instruction_set_en.pdf
 * 
 * The WiFi software somewhat convoluted.
 * 
 * In order to simplify operation in the field, each freETarget 
 * is a WiFi station.  The target is assigned an SSID corresponding 
 * to the name of the target, ex FET-WODEN.  This helps to link up 
 * the WiFI to the target.
 * 
 * Each esp01 is a server so that the PC connects to it over 
 * IP address 192.168.10.9:1090
 * 
 * Unfortunatly as a server, each ESP expects to see more than one
 * connection, so a transparent or passthrought mode is not possible.
 * Instead the incoming messages are tagged with a connection number
 * and outgoign messages are prepended with a connection number.
 * 
 * Thus the function esp01_receive constantly listens on the serial
 * port, parses the input and saves only the message to a 
 * circular buffer that is used later on by the application.
 * 
 * On output, the function esp01_send tells the esp01 to expect a 
 * very long null-terminated message.  The regular Serial.send()
 * messages are then used to send the body of the message and at 
 * the end esp01_send() inserts the null and kicks off the 
 * transmission.
 * 
 *---------------------------------------------------------------*/
#include "json.h"
#include "token.h"

/*
 * Function Prototypes
 */
static bool esp01_waitOK(unsigned int trace_on,unsigned int max_wait);   // Wait for an OK to come back
static void esp01_flush(void);          // Flush any pending messages

/*
 * Local Variables
 */
static volatile unsigned long wdt_tick; // Watchdog timer tick
static bool esp01_present = true;      // TRUE if the esp 01 is installed
static bool esp01_known = false;        // The state of the ESP is not known
static bool esp01_first = true;         // Start the first time through

static char esp01_in_queue[256];         // Place to store incoming characters
static int  esp01_in_ptr;               // Queue in pointer
static int  esp01_out_ptr;              // Queue out pointer

static bool esp01_connect[esp01_N_CONNECT]; // Set to true when a client (0-3) connects


// Wi-Fi test 1: one parser owns all ESP responses, including during sends.
// No callbacks or output_to_all() calls from this parser (avoids re-entry).
static char esp01_line[64];
static unsigned int esp01_line_len;
static bool esp01_line_overflow;
static unsigned long esp01_payload_left;
static bool esp01_payload_accept;
static bool esp01_greeting[esp01_N_CONNECT];
static unsigned long esp01_ok_seq, esp01_error_seq, esp01_send_seq, esp01_prompt_seq;
static unsigned long esp01_rx_overflows;
static char esp01_ip[esp01_IP_SIZE] = "0.0.0.0";
static bool esp01_query_ip;
static bool esp01_station_ready;
static bool esp01_server_ready;

static bool esp01_valid_ip(const char* s)
{
  for (unsigned int part=0; part<4; ++part)
  {
    unsigned int value=0, digits=0;
    while (*s >= '0' && *s <= '9')
    {
      if (++digits > 3) return false;
      value=value*10+(*s++-'0');
    }
    if (!digits || value>255) return false;
    if (part<3) { if (*s++ != '.') return false; }
    else if (*s != 0) return false;
  }
  return true;
}

static void esp01_parse_line(void)
{
  const char* line=esp01_line;
  if (!strcmp(line,"OK")) ++esp01_ok_seq;
  else if (!strcmp(line,"SEND OK")) ++esp01_send_seq;
  else if (!strcmp(line,"ERROR") || !strcmp(line,"FAIL") ||
           !strcmp(line,"SEND FAIL") || !strncmp(line,"busy",4)) ++esp01_error_seq;
  else if (!strcmp(line,"WIFI DISCONNECT") || !strcmp(line,"ready"))
  {
    esp01_station_ready=false;
    strcpy(esp01_ip,"0.0.0.0");
    for (unsigned int i=0;i<esp01_N_CONNECT;++i)
      esp01_connect[i]=esp01_greeting[i]=false;
    // ESP normally retains the server on a Wi-Fi disconnect. No blind retries.
    if (!strcmp(line,"ready")) esp01_server_ready=false;
  }
  if (line[0]>='0' && line[0]<'0'+esp01_N_CONNECT && line[1]==',')
  {
    unsigned int id=line[0]-'0';
    if (!strcmp(line+2,"CONNECT"))
    {
      esp01_connect[id]=true;
      esp01_greeting[id]=true;
    }
    else if (!strcmp(line+2,"CLOSED"))
      esp01_connect[id]=esp01_greeting[id]=false;
  }
  if (esp01_query_ip)
  {
    const char* value=0;
    const char* prefixes[]={"+CIPSTA_CUR:ip:\"", "+CIPSTA:ip:\"",
                            "+CIPAP_CUR:ip:\"", "+CIPAP:ip:\""};
    for (unsigned int i=0;i<4;++i)
      if (!strncmp(line,prefixes[i],strlen(prefixes[i]))) value=line+strlen(prefixes[i]);
    if (value)
    {
      const char* end=strchr(value,'"');
      if (end && end[1]==0 && (unsigned int)(end-value)<esp01_IP_SIZE)
      {
        char candidate[esp01_IP_SIZE];
        memcpy(candidate,value,end-value); candidate[end-value]=0;
        if (esp01_valid_ip(candidate)) strcpy(esp01_ip,candidate);
      }
    }
  }
}

static void esp01_feed(char ch)
{
  if (esp01_payload_left)
  {
    if (esp01_payload_accept)
    {
      int next=(esp01_in_ptr+1)%sizeof(esp01_in_queue);
      if (next==esp01_out_ptr)
      {
        ++esp01_rx_overflows;
        esp01_payload_accept=false;
        // Do not overwrite unread command bytes.
      }
      else { esp01_in_queue[esp01_in_ptr]=ch; esp01_in_ptr=next; }
    }
    --esp01_payload_left;
    return;
  }
  if (ch=='>' && esp01_line_len==0) { ++esp01_prompt_seq; return; }
  if (ch=='\r') return;
  if (ch=='\n')
  {
    esp01_line[esp01_line_len]=0;
    if (!esp01_line_overflow) esp01_parse_line();
    esp01_line_len=0; esp01_line_overflow=false;
    return;
  }
  // ESP prompt is followed by an optional space, not a response line.
  if (ch==' ' && esp01_line_len==0) return;
  if (ch==':' && !esp01_line_overflow && !strncmp(esp01_line,"+IPD,",5))
  {
    esp01_line[esp01_line_len]=0;
    const char* v=esp01_line+5;
    unsigned long id=0, length=0;
    unsigned int digits=0;
    while (*v>='0' && *v<='9') { if (++digits>1) break; id=id*10+(*v++-'0'); }
    bool valid=digits==1 && *v==',';
    if (valid)
    {
      ++v; digits=0;
      while (*v>='0' && *v<='9')
      {
        if (++digits>5) { valid=false; break; }
        length=length*10+(*v++-'0');
      }
      valid=valid && digits && *v==0 && length<=65535UL;
    }
    if (valid)
    {
      esp01_payload_left=length;
      unsigned int free_bytes=(esp01_out_ptr-esp01_in_ptr-1+sizeof(esp01_in_queue))%sizeof(esp01_in_queue);
      esp01_payload_accept=id<esp01_N_CONNECT && length<=free_bytes;
      if (id<esp01_N_CONNECT && length>free_bytes) ++esp01_rx_overflows;
      esp01_line_len=0;
      return;
    }
  }
  if (esp01_line_len<sizeof(esp01_line)-1)
  { esp01_line[esp01_line_len++]=ch; esp01_line[esp01_line_len]=0; }
  else esp01_line_overflow=true;
}

static void esp01_pump(void)
{
  while (aux_spool_available()) esp01_feed(aux_spool_read());
}

static bool esp01_wait_event(unsigned long* event, unsigned long previous,
                             unsigned long errors, unsigned long timeout)
{
  unsigned long start=millis();
  while ((unsigned long)(millis()-start)<timeout)
  {
    esp01_pump();
    if (esp01_error_seq!=errors) return false;
    if (*event!=previous) return true;
  }
  return false;
}

// Escape AT string metacharacters without exposing credentials in USB diagnostics.
static void esp01_print_quoted(const char* value)
{
  while (*value)
  {
    if (*value=='"' || *value=='\\' || *value==',') AUX_SERIAL.print('\\');
    AUX_SERIAL.print(*value++);
  }
}

/*----------------------------------------------------------------
 *
 * function: void esp01_init
 *
 * brief: Initialize the esp01
 * 
 * return: esp_present - set to TRUE if an esp01 is on the board
 *
 *----------------------------------------------------------------
 *   
 * The function outputs a series of AT commands to the port to 
 * 
 * Set the part as a WiFi Server
 *    The SSID is set up as FET-<name>
 *    The freETarget IP address is 192.169.10.9
 *    The freETarget port is 1090
 *    The connecting PC will be assigned address 192.168.10.8
 *    
 * Open a port for connection
 * 
 * IMPORTANT
 * 
 * The init function does not set the pass through mode.  This
 * is done by a separate call to esp01_passthrough();
 * 
 * Network Settings
 * 
 * json_wifi_ssid given:
 *    Connect to this SSID
 *    use it's DHCP server
 *    Use json_wifi_ip if given
 *    
 * json_wifi_ssid empty:
 *    I am the SSID
 *    I am the DHCP server
 *    Use 192.168.10.9 as my IP address
 *   
 *--------------------------------------------------------------*/
void esp01_init(void)
{  
  if ( DLT(DLT_CRITICAL) ) 
  {
    Serial.print(T("esp01_init()"));
  }
  
  timer_new(&wdt_tick, 0);                    // Setup the timers in-case it is needed for diagnostics later
  
  if ( json_token != TOKEN_WIFI )             // The connector is used for token ring
  {
    if ( DLT(DLT_CRITICAL) ) 
    {
      Serial.print(T("In Token Ring mode. esp01 not available"));
    }
    return;
  }
  
  esp01_server_ready=esp01_station_ready=false;
  esp01_line_len=0; esp01_line_overflow=false; esp01_payload_left=0;
  esp01_in_ptr=esp01_out_ptr=0;
  for (unsigned int i=0;i<esp01_N_CONNECT;++i) esp01_greeting[i]=false;
  esp01_first = true;                         // First time through
  esp01_known = true;                         // Assume that one exists
  esp01_reset();
  esp01_flush();
  
/*
 * Determine if the esp01 is attached to the Accessory Connector
 */
  if (esp01_is_present() == false )
  {
    if ( DLT(DLT_CRITICAL) ) 
    {
      Serial.print(T("esp01: Not Found"));
    }
    return;                                     // No hardware installed, nothing to do
  }

  if ( DLT(DLT_CRITICAL) )
  {
    Serial.print(T("esp01: Present"));
  }
  
  json_token = TOKEN_WIFI;                     // If WiFi is present, then the TOKEN ring is disabled
  
/*
 * There is an esp01 on the freETarget.  We need to program it
 */
  AUX_SERIAL.print(T("ATE0\r\n"));                   // Turn off echo (don't use it)
  if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false) && DLT(DLT_CRITICAL) )
  {
    Serial.print(T("esp01: Failed ATE0"));
  }

  AUX_SERIAL.print(T("AT+RFPOWER=80\r\n"));          // Set max power
  if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false) && DLT(DLT_CRITICAL))
  {
    Serial.print(T("esp01: Failed AT+RFPOWER=80"));  
  } 

  esp01_flush();
/*
 * If an SSID is defined, then we are connecting to an existing access point
 */
  if ( *json_wifi_ssid == 0 )                           // If the SSID is empty, then we are an SSID and a DHCP server and our IP address is 192.168.10.9
  {                                                     // ******************************
    if ( DLT(DLT_CRITICAL) )
    {
      Serial.print(T("esp01: Configuring as an SSID"));
    }
      
    AUX_SERIAL.print(T("AT+CWMODE_DEF=2\r\n"));        // We want to be a soft access point
    if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false) && DLT(DLT_CRITICAL) )
    {
      Serial.print(T("esp01: Failed AT+CWMODE_DEF=2"));
    }
    
    AUX_SERIAL.print(T("AT+CWSAP_DEF=\"FET-")); AUX_SERIAL.print(namesensor[json_name_id]); AUX_SERIAL.print(T("\",\"NA\",")); AUX_SERIAL.print(json_wifi_channel); AUX_SERIAL.print(T(",0\r\n"));
    if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false) && DLT(DLT_CRITICAL) )
    {
      Serial.print(T("esp01: Failed AT+CWSAP_DEF=\"FET-")); Serial.print(namesensor[json_name_id]); Serial.print(T("\",\"NA\",")); Serial.print(json_wifi_channel); Serial.print(T(",0\r\n"));
    }  
    
    AUX_SERIAL.print(T("AT+CIPAP_DEF=\"192.168.10.9\",\"192.168.10.9\"\r\n")); // Set the freETarget IP to 192.168.10.9
    if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false) && DLT(DLT_CRITICAL) )
    {
      Serial.print(T("\r\nesp01: Failed AT+CIPAP_DEF=\"192.168.10.9\",\"192.168.10.9\""));
    }
      
    AUX_SERIAL.print(T("AT+CWDHCP_DEF=0,1\r\n"));      // DHCP turned on
    if ( (esp01_waitOK(0,esp01_MAX_WAITOK) == false ) && DLT(DLT_CRITICAL) )
    {
      Serial.print(T("esp01: Failed AT+CWDHCP_DEF=0,1"));
    }

  }                                                     // ******************************
  else                                                  // Connect to an SSID, let it define the DHCP if needed
  {
    if ( DLT(DLT_CRITICAL) )
    {
      Serial.print(T("esp01: Connecting to an access point: ")); Serial.print(json_wifi_ssid);
    }
    
    AUX_SERIAL.print(T("AT+CWMODE_DEF=1\r\n"));
    if (!esp01_waitOK(0,esp01_MAX_WAITOK))
    { Serial.println(T("[WIFI] STA mode command failed")); return; }
    // Explicitly enable station DHCP; AP uses a separate setting (mode 0).
    AUX_SERIAL.print(T("AT+CWDHCP_CUR=1,1\r\n"));
    if (!esp01_waitOK(0,esp01_MAX_WAITOK))
    { Serial.println(T("[WIFI] Station DHCP command failed")); return; }
    bool joined=false;
    for (unsigned int attempt=0; attempt<2 && !joined; ++attempt)
    {
      AUX_SERIAL.print(T("AT+CWJAP_DEF=\"")); esp01_print_quoted(json_wifi_ssid);
      AUX_SERIAL.print(T("\",\"")); esp01_print_quoted(json_wifi_pwd);
      AUX_SERIAL.print(T("\"\r\n"));
      if (esp01_waitOK(0,30000U))
      {
        char address[esp01_IP_SIZE];
        esp01_myIP(address);
        joined=strcmp(address,"0.0.0.0")!=0;
      }
      if (!joined) Serial.println(T("[WIFI] STA join/IP check failed"));
    }
    esp01_station_ready=joined;
    if (!joined) return; // Do not report success or start an unusable server.
    Serial.print(T("[WIFI] STA IP ")); Serial.print(esp01_ip); Serial.println(T(":1090"));

  }

/*
 * Other operating settings
 */
  AUX_SERIAL.print(T("AT+CIPMODE=0\r\n"));           // Normal Transmission Mode
  if ( (esp01_waitOK(1,esp01_MAX_WAITOK) == false ) && DLT(DLT_CRITICAL) )
  {
    Serial.print(T("esp01: Failed AT+CIPMODE=0"));
  }
  
  AUX_SERIAL.print(T("AT+CIPMUX=1\r\n"));
  if (!esp01_waitOK(0,esp01_MAX_WAITOK))
  { Serial.println(T("[WIFI] CIPMUX failed")); return; }
  AUX_SERIAL.print(T("AT+CIPSERVER=1,1090\r\n"));
  if (!esp01_waitOK(0,esp01_MAX_WAITOK))
  { Serial.println(T("[WIFI] TCP server failed")); return; }
  esp01_server_ready=true;
  AUX_SERIAL.print(T("AT+CIPSTO=0\r\n")); // Disable idle timeout for a scoring session.
  esp01_waitOK(0,esp01_MAX_WAITOK);
  Serial.println(T("[WIFI] TCP server ready on port 1090"));

/*
 * All done, return
 */
  if ( DLT(DLT_CRITICAL) )
  {
    Serial.print(T("esp01: Initialization complete"));
  }

  return;
}


/*----------------------------------------------------------------
 *
 * function: void esp01_reset
 *
 * brief:    Take control of the ESP and issue a reset
 * 
 * return:   TRUE if the module acknowleges the command and restarts
 *
 *----------------------------------------------------------------
 *   
 * We don't know what state the ESP is in, so this function
 * isses +++AT to get contol of the device and reset it to 
 * factory defaults. 
 *   
 *--------------------------------------------------------------*/
static bool esp01_reset(void)
{
  unsigned int i;

  if ( json_token != TOKEN_WIFI )
  {
    return false;
  }

  if ( DLT(DLT_CRITICAL) )
  {
    Serial.print(T("esp01: Resetting esp01"));
  }
  
/*
 * Send out the break then restart the module
 */
  esp01_flush();
  AUX_SERIAL.print(T("+++"));
  delay(ONE_SECOND);
  AUX_SERIAL.print(T("AT+RST\r\n"));
  if (!esp01_waitOK(0,esp01_MAX_WAITOK))
  {
    Serial.println(T("[WIFI] ESP reset did not acknowledge"));
    return false;
  }

/*
 * Flush the stuff from the self test
 */
  delay(ONE_SECOND);
  esp01_flush();
  
/*
 * All done, 
 */
  for (i=0; i != esp01_N_CONNECT; i++)
  {
    esp01_connect[i] = false;
  }
  
  return true;
}


/*----------------------------------------------------------------
 *
 * function: bool esp01_is_present
 *
 * brief:    Determines if an esp01 is installed
 * 
 * return:   TRUE if the ESO-01 is installed
 *
 *----------------------------------------------------------------
 *   
 * The function outputs an AT<entere> to the auxilarry port and
 * waits to see if an OK is returned within one second.
 * 
 * This function can only be executed once after a reset.  After 
 * that time, the device may be in pass through mode and will not
 * do anything with the AT command
 *   
 *--------------------------------------------------------------*/

bool esp01_is_present(void)
{
  if ( esp01_known == false )             // The ESP is known not to exist
  {
    return 0;                             // Say it is not present
  }
  
/*
 * If the function has been exectued once, return the old results 
 */
  if ( esp01_first == false )
  {
    return esp01_present;
  }

/*
 * Determine if the esp01 is attached to the Accessory Connector
 */
  esp01_present = false;                  // Assume that the esp01 is not installed
  
  esp01_flush();                          // Eat any garbage that might be on the port

  AUX_SERIAL.print(T("+++"));
  delay(ONE_SECOND);
  AUX_SERIAL.print(T("AT\r\n"));            // Send out an AT command to the port
  esp01_present = esp01_waitOK(0,esp01_MAX_WAITOK);         // and wait for the OK to come back

/*
 * All done, return the esp01 present state
 */
  esp01_first = false;                   // Done it once.
  return esp01_present;
}


/*----------------------------------------------------------------
 *
 * function: bool esp01_test
 *
 * brief:    Tests to see if the WiFi responds to ATs
 * 
 * return:   Displayed on screen
 *
 *----------------------------------------------------------------
 *   
 * The function outputs an AT<entere> to the auxilarry port and
 * waits to see if an OK is returned within one second.
 * 
 * This function can only be executed once after a reset.  After 
 * that time, the device may be in pass through mode and will not
 * do anything with the AT command
 *   
 *--------------------------------------------------------------*/
void esp01_echo(void)
{
  char ch;                                  // Character read from esp01
  
  timer_new(&wdt_tick, esp01_MAX_WAITOK);
 
  while ( wdt_tick )
  {
    delay(1);
    if ( aux_spool_available() != 0 ) 
    {
      ch = aux_spool_read();
      Serial.print(ch);
      wdt_tick = esp01_MAX_WAITOK;
    }
  }

  return;
}

void esp01_test(void)
{
  timer_new(&wdt_tick, 0);                // Setup the timers in-case it is needed for diagnostics later
  
  esp01_flush();                          // Eat any garbage that might be on the port

  if ( esp01_is_present() == false )
  {
    Serial.print(T("\n\resp01 not present. Continuing test anyway")); 
  }

/*
 * Send out status commands
 */
 
  Serial.print(T("\n\rResetting esp01\n\r"));
  AUX_SERIAL.print(T("+++"));
  delay(ONE_SECOND * 1.1);
  AUX_SERIAL.print(T("AT+RST\r\n"));
  esp01_echo();
    
  Serial.print(T("\r\nSoftware Version\r\n"));
  AUX_SERIAL.print(T("AT+GMR\r\n"));         // Send out an AT command to the port
  esp01_echo();

  Serial.print(T("\r\nList of SSIDs\r\n"));
  AUX_SERIAL.print(T("AT+CWLAP\r\n"));       // Send out an AT command to the port
  esp01_echo();
    
/*
 * Initialize the WiFi if available
 */
   set_LED('*', '*', '.');                 // Hello World
   Serial.print(T("\r\nReinitializing esp01\r\n")); 
   esp01_init();                           // Prepare the WiFi channel if installed
   
/*
 * All done, return the esp01 present state
 */
  Serial.print(T("\r\nTest Over"));
  return;
}


/*----------------------------------------------------------------
 *
 * function: bool esp01_status
 *
 * brief:    Request and display stauts
 * 
 * return:   Displayed on screen
 *
 *----------------------------------------------------------------
 *   
 * The function issues a status command and sees what comes back
 * then it issues a PING on the four IP addressees that should
 * be attached to is.
 *--------------------------------------------------------------*/

static char* status_list[] = {"CWMODE_DEF",  "CWSAP_DEF", "CWJAP_DEF",
                              "CWDHCP_DEF",  "CIPAP_DEF", "CIPSTA_CUR",
                              "CWDHCPS_DEF", "CIPMODE",    "CIPSERVER",
                              "CIPMUX",      "CIPSTO", 0};        // Status List

void esp01_status(void)
{
  char ch;                                // Character read from esp01
  unsigned int i;
  char str[32];
  
/*
 * Get the status of the connection
 */
  Serial.print(T("\n\resp01_status\r\n"));

  AUX_SERIAL.print(T("+++"));
  delay(ONE_SECOND + ONE_SECOND/10);
  AUX_SERIAL.print(T("AT+CIPSTATUS\r\n"));

  timer_new(&wdt_tick, esp01_MAX_WAITOK);
  while ( wdt_tick  )
  {
    if ( aux_spool_available() != 0 ) 
    {
      ch = aux_spool_read();                  // Echo what comes back
      Serial.print(ch);
      wdt_tick = esp01_MAX_WAITOK;
    }
  }

/*
 * All of the settings
 */
  i=0;
  while (status_list[i] != 0)
  {
    Serial.print(T("\r\nStatus: ")); Serial.print(status_list[i]); Serial.print(T("\r\n"));
    AUX_SERIAL.print(T("AT+")); AUX_SERIAL.print(status_list[i]); AUX_SERIAL.print(T("?\r\n"));
    timer_new(&wdt_tick, esp01_MAX_WAITOK);
    
    while ( wdt_tick )
    {
      if ( aux_spool_available() != 0 ) 
      {
        ch = aux_spool_read();                  // Echo what comes back
        Serial.print(ch);
        wdt_tick = esp01_MAX_WAITOK;
      }
    }
    i++;
  }
  
/*
 * Ping and see what comes back
 */
  Serial.print(T("\n\resp01_ping\r\n"));

  for (i=0; i != esp01_N_CONNECT; i++)
  {
    AUX_SERIAL.print(T("+++"));
    delay(ONE_SECOND + ONE_SECOND/10);
    sprintf(str, "AT+PING=\"192.168.10.%d\"\r\n", i);
    AUX_SERIAL.print(str);
    Serial.print(str);
    wdt_tick = esp01_MAX_WAITOK;
    while ( wdt_tick )
    {
      if ( aux_spool_available() != 0 ) 
      {
        ch = aux_spool_read();
        Serial.print(ch);
        wdt_tick = esp01_MAX_WAITOK;
      }
    }
  }
  
/*
 * All done, return the esp01 present state
 */
  Serial.print(T("\r\nDone\r\n"));
  return;
}


/*----------------------------------------------------------------
 *
 * function: bool esp01_myIP
 *
 * brief:    Obtain the current IP address
 * 
 * return:   Returned to a pointer
 *
 *----------------------------------------------------------------
 *   
 * The function issues a status command and sees what comes back
 * then it issues a PING on the four IP addressees that should
 * be attached to is.
 *--------------------------------------------------------------*/
void esp01_myIP(char* return_value)
{
  strcpy(esp01_ip,"0.0.0.0");
  esp01_query_ip=true;
  if (*json_wifi_ssid==0) AUX_SERIAL.print(T("AT+CIPAP_CUR?\r\n"));
  else AUX_SERIAL.print(T("AT+CIPSTA_CUR?\r\n"));
  bool ok=esp01_waitOK(0,esp01_MAX_WAITOK);
  esp01_query_ip=false;
  if (!ok) strcpy(esp01_ip,"0.0.0.0");
  strcpy(return_value,esp01_ip); // caller must provide esp01_IP_SIZE bytes
}

/*----------------------------------------------------------------
 *
 * function: void esp01_flush
 *
 * brief:    Flush any characters waiting in the buffer
 * 
 * return:   None
 *
 *----------------------------------------------------------------
 *   
 *   Just read the port and return when nothing is left 
 *   
 *--------------------------------------------------------------*/

 static void esp01_flush(void)
 {
   while ( aux_spool_available() != 0 ) 
   {
    aux_spool_read();
   }

 /*
  * The buffer is empty, go home
  */
   return;
 }


/*----------------------------------------------------------------
 *
 * function: bool esp01_waitOK(0,esp01_MAX_WAITOK)
 *
 * brief:    Wait for the OK to come back
 * 
 * return:   FALSE if no OK came back
 *
 *----------------------------------------------------------------
 *   
 *   The function has a list of expected messsages and responses
 *   
 *   As each character is received, it is compared to the list and
 *   when it reaches the end of the list the value is returned
 *   
 *--------------------------------------------------------------*/

static bool esp01_waitOK(unsigned int trace_on, unsigned int wait_time)
{
  // Only a complete final OK line acknowledges a command. GOT IP is an event.
  return esp01_wait_event(&esp01_ok_seq,esp01_ok_seq,esp01_error_seq,wait_time);
}

/*----------------------------------------------------------------
 *
 * function: char esp01_read()
 *
 * brief:    Return a character from the Accessory port
 * 
 * return:   Next character waiting
 *
 *----------------------------------------------------------------
 *   
 *   The function checks to see if an esp01 is attached to the
 *   board.  
 *   
 *   Not attached - Perform regular WIFI_SERIAL.read()
 *   Attached     - Take a character from the IP queue
 *   
 *--------------------------------------------------------------*/

char esp01_read(void)
{
  char ch;                              // Working character
  
/*
 * Determine which source will be used to get the next character
 */
  if ( esp01_is_present() == false )
  {
    ch = aux_spool_read();
    return ch;                          // Just do a regular read from the aux port
  }

/*  
 *   We have an esp01 attached,  Get the character from the queue
 */
  if ( esp01_in_ptr == esp01_out_ptr )  // Is the queue empty?
  {
    ch = -1;                            // Return an error
  }
  else
  {
    ch = esp01_in_queue[esp01_out_ptr]; // Get the character out of the queueu
    esp01_out_ptr = (esp01_out_ptr + 1) % sizeof(esp01_in_queue);// increment and wrap around
  }

/*
 * All done, return the next character
 */
  return ch;
}

/*----------------------------------------------------------------
 *
 * function: unsigned int esp01_available_all)
 *
 * brief:    Determine ihow many characters are available
 * 
 * return:   Number of characters in the input queue
 *
 *----------------------------------------------------------------
 *   
 *   The function checks to see if an esp01 is attached to the
 *   board.  
 *   
 *   Not attached - Perform regular WIFI_SERIAL.gavailable_all)
 *   Attached     - Return the queue size
 *   
 *--------------------------------------------------------------*/

unsigned int esp01_available(void)
{
  unsigned int x;                       // Working character
  
/*
 * Determine which source will be used to get return the input size
 */
  if ( esp01_is_present() == false )
  {
    return aux_spool_available();           // Chars available if in != out
  }

/*  
 *   We have an esp01 attached,  Figure out the bytes in the queueu
 */
  if ( esp01_in_ptr < esp01_out_ptr )   // Have we wrapped around?
  {
    x = sizeof(esp01_in_queue) + esp01_in_ptr;  // add in the size offset
  }
  else
  {
    x = esp01_in_ptr;
  }

  x -= esp01_out_ptr;                   // Subtract the output pointer


/*
 * All done, return
 */
  return x;
}


/*----------------------------------------------------------------
 *
 * function: char esp01_send()
 *
 * brief:    Send a string over the IP port
 * 
 * return:   TRUE if the connection is active
 *
 *----------------------------------------------------------------
 *   
 *   The function checks to see if an esp01 is attached to the
 *   board.  
 *   
 *   Not attached - Do nothing
 *   Attached     - Output the control bytes to begin IP transmission
 *   
 *   The function operates on a bit of a kluge.  The esp01 has a 
 *   command AT+CIPSENDEX which will transmit the next N bytes 
 *   over the IP connection. The esp01 will also stop collecting 
 *   bytes and send the data if a NULL is received.
 *   
 *   The function uses a state machine
 *   
 *   Not ready to send out characters
 *   Filling the transmit buffer
 *   Kicking out the transmit buffer.
 *   
 *   This lets the application fill the tranmsit buffer as 
 *   quickly as possible until the buffer is full.
 *   
 *   The appplication must send a null to trigger the sending
 *   operation.
 *--------------------------------------------------------------*/
bool esp01_send_ch(char ch, int connection)
{
  char str[2]={ch,0};
  return esp01_send(str,connection);
}

bool esp01_send(char* str, int connection)
{
  if (!str || connection<0 || connection>=esp01_N_CONNECT) return false;
  esp01_pump(); // Preserve commands and connection notifications arriving during output.
  if (!esp01_connect[connection]) return false;
  size_t remaining=strlen(str);
  if (!remaining) return true;
  while (remaining)
  {
    unsigned int len=remaining>esp01_BUFFER_SIZE ? esp01_BUFFER_SIZE : remaining;
    char command[32];
    unsigned long prompt=esp01_prompt_seq, errors=esp01_error_seq;
    sprintf(command,"AT+CIPSEND=%d,%u\r\n",connection,len);
    AUX_SERIAL.print(command);
    if (!esp01_wait_event(&esp01_prompt_seq,prompt,errors,esp01_MAX_WAITOK))
    {
      // Missing prompt leaves uncertain data mode. Do not send another AT command.
      esp01_connect[connection]=false;
      Serial.println(T("[WIFI] Send prompt missing; restart target before reconnecting"));
      return false;
    }
    unsigned long sent=esp01_send_seq;
    errors=esp01_error_seq;
    set_LED(LED_WIFI_SEND);
    AUX_SERIAL.write((const uint8_t*)str,len); // Exactly the length announced, in order.
    if (!esp01_wait_event(&esp01_send_seq,sent,errors,esp01_MAX_WAITOK))
    {
      esp01_connect[connection]=false;
      Serial.println(T("[WIFI] SEND OK missing; no automatic replay"));
      return false; // Never duplicate an ambiguously delivered shot fragment.
    }
    str+=len; remaining-=len;
  }
  set_LED(LED_READY);
  return true;
}

/*----------------------------------------------------------------
 *
 * function: char esp01_receive()
 *
 * brief:    Receive a string over the IP port
 * 
 * return:   Incoming characters saved to a queueu
 *
 *----------------------------------------------------------------
 *   
 *   The esp01 receives incoming characters on the IP connection, 
 *   parses the frame, and informs the application of what 
 *   connection received data, the length, and the contents
 *   
 *   ex
 *   
 *   +IPD,l,p:d         // IP-Data comes in from the target
 *                      // l - length
 *                      // p - port
 *                      // d - data
 *   0,CONNECT          // The target connects to the PC
 *   
 *   As with any IP type communications, there is a disconnect
 *   between what is sent and what is received.  In many cases 
 *   the sent data may be broken up over several received frames
 *   
 *   This function is a state machine that parses the incoming
 *   message and then buffers only the 'real' data so that it 
 *   can be extracted later on.
 *   
 *   While this ESP software keeps track of what connection is
 *   connected, esp01_receive() merges all of the connections into
 *   a single input stream.
 *   
 *--------------------------------------------------------------*/

void esp01_receive(void)
{
  if (!esp01_is_present()) return;
  esp01_pump();
  // Defer handshakes until the parser is idle; send callbacks also pump input.
  for (unsigned int i=0;i<esp01_N_CONNECT;++i)
  {
    if (esp01_greeting[i] && esp01_connect[i])
    {
      esp01_greeting[i]=false;
      POST_version();
      show_echo();
    }
  }
}

/*----------------------------------------------------------------
 *
 * function: bool esp01_connected()
 *
 * brief:    Return the connection status
 * 
 * return:   TRUE if any connection is connected
 *
 *----------------------------------------------------------------
 *   
 *   Loops throught the available connections and ORs together the
 *   status of each connection
 *   
 *--------------------------------------------------------------*/
bool esp01_connected(void)
{ 
  unsigned int i;
  bool return_value;

  return_value = false;

  for (i=0; i != esp01_N_CONNECT; i++)
  {
    return_value |= esp01_connect[i];
  }
  
  return return_value;
}

/*----------------------------------------------------------------
 *
 * function: bool esp01_close()
 *
 * brief:    Close the open connections
 * 
 * return:   Nothing
 *
 *----------------------------------------------------------------
 *   
 *   Close the connection associated with this connection (connection)
 *   
 *   
 *--------------------------------------------------------------*/
void esp01_close(unsigned int connection)
{
  if (connection>=esp01_N_CONNECT || !esp01_is_present()) return;
  char command[32];
  esp01_connect[connection]=esp01_greeting[connection]=false;
  sprintf(command,"AT+CIPCLOSE=%u\r\n",connection);
  AUX_SERIAL.print(command);
  esp01_waitOK(0,esp01_MAX_WAITOK);
}
