# Optional Firmware — freETarget 4.2.8 WiFi Test 1 / LED PWM 13

## Identity and purpose

This source archive was explicitly confirmed by the developer as the **final firmware source used on their working Arduino Minimalist target**. It is byte-for-byte identical to the earlier `freETarget_WiFi_LED_Pin13.zip` record in the companion package, itself based on the supplied `freETarget_WiFi_Test_1(1).zip` source. Its `freETarget.h` identifies it as **4.2.8 WiFi Test 1**. Its `analog_io.h` defines `LED_PWM` as **13**, not the upstream/default **5**. The supplied record states that **only** this pin assignment was changed from WiFi Test 1; the earlier Wi-Fi station-mode work is retained.

The WiFi Test 1 source includes changes for station-mode DHCP (`AT+CWDHCP_CUR=1,1`), SSID join/IP checks, response parsing, and server setup on TCP **1090**. It also supports an access-point configuration when no network SSID is set (target AP IP **192.168.10.9**). The source is for the **Arduino Mega 2560 freETarget sketch**, which controls an ESP-01 AT-command Wi-Fi module. It is **not** an ESP-01 firmware image.

## Source review note: duplicate LED_PWM definitions

The supplied source also contains a legacy `#define LED_PWM 5` in `gpio.h`, while `analog_io.h` defines `LED_PWM 13`. In the main `freETarget.ino` include order, `analog_io.h` comes after `gpio.h`, so pin 13 is the last definition; this may produce a compiler redefinition warning. **This closed-beta package preserves the developer-confirmed firmware source unchanged**. Do not assume it has been independently compiled or validated on other wiring revisions.

## Important limitations

- **Do not flash by default.** Test the desktop app with the target's existing, functioning firmware first.
- **Hardware-specific LED pin:** pin 13 is the developer's wiring. On targets using LED PWM pin 5 or other wiring, this build can leave illumination nonfunctional. Confirm wiring and board revision first.
- The ZIP contains **source only**, not a compiled `.hex` or ready-to-flash binary. The developer confirms this is their final running firmware source and reports a working Minimalist target. The archived source has **not been independently compiled and compared against a readback of the flashed binary**, so exact binary identity is not independently verified.
- Arduino board selection from the source README: **Arduino Mega 2560**. Verify that your particular Minimalist controller uses this board before attempting any upload.
- Flashing can affect device operation and saved configuration. Preserve your working firmware and Wi-Fi settings before experimenting. If you cannot verify the board/pin wiring, **do not flash**.
- Firmware changes are not required for ordinary Windows app installation. Do not flash another manufacturer's target or a non-Minimalist build on the basis of this ZIP.

## For compatible users who elect to compile

1. Confirm board type, LED pin, and compatible ESP-01 AT firmware first.
2. Extract the nested firmware ZIP. In Arduino IDE, open `source/freETarget/freETarget.ino` and select **Arduino Mega 2560** and the correct port.
3. **Verify/Compile** before uploading. Address any board/library/compiler errors; do not guess at pin substitutions.
4. Only after confirming a safe rollback path, **Upload** to the target controller. Recheck LED brightness and Wi-Fi behavior in the desired mode.
5. For station mode, use the IP address assigned by the tester's router and port 1090. For target access-point mode, connect to the target's `FET-...` Wi-Fi network and use `192.168.10.9:1090` if the target is configured as in this source.
6. Record the exact firmware revision and hardware pin mapping in your bug report.

## Rights and attribution

Derived from the freETarget project by the ten-point-nine project. Its original MIT copyright/license text is included in `LICENSES/freETarget_MIT.txt`. Modified Wi-Fi Test 1 code and the LED PWM pin-13 change should be identified as modified builds, not presented as the official firmware.
