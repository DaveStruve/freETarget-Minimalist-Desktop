"""freETarget v1.7.9 local TCP / USB serial bridge. Python 3.10+.
USB requires pyserial==3.5; TCP works without it. Target commands use the active connection and are never replayed on reconnect.
"""
import codecs
import json
import math
import pathlib
import re
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None

ROOT = pathlib.Path(__file__).resolve().parent
lock = threading.RLock()
state = dict(connected=False, connecting=False, message='Disconnected', events=[], next_id=1,
             generation=0, resource=None, cancel=None, config=None, identity=None,
             bytes_received=0, raw_packets=0, parse_errors=0, successful_config=None,
             target_settings=None, settings_event_id=0, connection_epoch=0)


def push(event, generation=None):
    with lock:
        if generation is not None and generation != state['generation']:
            return
        event = dict(event, id=state['next_id'])
        state['next_id'] += 1
        state['events'].append(event)
        state['events'] = state['events'][-2000:]


TARGET_PROTOCOL = json.loads('{"firmware": "4.2.8 WiFi Test 1", "commands": ["ANGLE", "BYE", "CALIBREx10", "DELAY", "DIP", "DOPPLER", "ECHO", "FACE_STRIKE", "FOLLOW_THROUGH", "INIT", "KEEP_ALIVE", "LED_BRIGHT", "MFS", "MFS2", "MIN_RING_TIME", "NAME_ID", "NEW", "NONVOL_BACKUP", "NONVOL_RESTORE", "PAPER_ECO", "PAPER_TIME", "POWER_SAVE", "RAPID_COUNT", "RAPID_ENABLE", "RAPID_TIME", "RAPID_WAIT", "RESET", "RH", "SEND_MISS", "SENSOR", "SN", "STEP_COUNT", "STEP_TIME", "TABATA_ENABLE", "TABATA_ON", "TABATA_REST", "TABATA_WARN_OFF", "TABATA_WARN_ON", "TARGET_TYPE", "TEST", "TOKEN", "TRACE", "VERSION", "WIFI_CHANNEL", "WIFI_PWD", "WIFI_SSID", "Z_OFFSET", "NORTH_X", "NORTH_Y", "EAST_X", "EAST_Y", "SOUTH_X", "SOUTH_Y", "WEST_X", "WEST_Y", "TA", "TB", "TC", "TD"], "safeCommands": ["ECHO", "VERSION"], "unavailable": ["CAL", "X_OFFSET", "Y_OFFSET"], "fields": {"NAME_ID": {"min": 0, "max": 30, "integer": true}, "PAPER_TIME": {"min": 0, "max": 2000, "integer": true}, "STEP_COUNT": {"min": 0, "max": 32767, "integer": true}, "STEP_TIME": {"min": 0, "max": 2000, "integer": true}, "LED_BRIGHT": {"min": 0, "max": 100, "integer": true}, "SENSOR": {"min": 0.1, "max": 2000, "integer": false}, "Z_OFFSET": {"min": -32768, "max": 32767, "integer": true}, "NORTH_X": {"min": -32768, "max": 32767, "integer": true}, "NORTH_Y": {"min": -32768, "max": 32767, "integer": true}, "EAST_X": {"min": -32768, "max": 32767, "integer": true}, "EAST_Y": {"min": -32768, "max": 32767, "integer": true}, "SOUTH_X": {"min": -32768, "max": 32767, "integer": true}, "SOUTH_Y": {"min": -32768, "max": 32767, "integer": true}, "WEST_X": {"min": -32768, "max": 32767, "integer": true}, "WEST_Y": {"min": -32768, "max": 32767, "integer": true}}, "names": ["TARGET", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "DOC", "DOPEY", "HAPPY", "GRUMPY", "BASHFUL", "SNEEZEY", "SLEEPY", "RUDOLF", "DONNER", "BLITZEN", "DASHER", "PRANCER", "VIXEN", "COMET", "CUPID", "DUNDER", "ODIN", "WODEN", "THOR", "BALDAR"], "maxWireBytes": 220}')

# Command protocol verified against the user's 4.2.8 WiFi Test 1 source.
write_lock = threading.RLock()
settings_changed = threading.Condition(lock)

def _command_object(command):
    if isinstance(command, str):
        if command.strip() == '?':
            # The Arduino's native status query is an unambiguous, read-only command.
            return '?', b'?\n'
        command = json.loads(command, parse_constant=reject_constant)
    if not isinstance(command, dict) or not command:
        raise ValueError('Enter one non-empty JSON command object.')
    for key, value in command.items():
        if not re.fullmatch(r'[A-Z][A-Za-z0-9_]{0,39}', key):
            raise ValueError('Invalid firmware command name.')
        if key in TARGET_PROTOCOL['unavailable']:
            raise ValueError(key + ' is not supported by the supplied 4.2.8 firmware.')
        if isinstance(value, bool):
            command[key] = int(value)
        elif isinstance(value, (int, float)):
            if not math.isfinite(value):
                raise ValueError('Command numbers must be finite.')
        elif isinstance(value, str):
            if any(ord(c) < 32 or ord(c) > 126 or c in '{}?^%*\\"' for c in value):
                raise ValueError('This firmware does not safely accept control characters, braces or JSON escapes in string values.')
        else:
            raise ValueError('Firmware values must be numeric or plain text.')
    wire = json.dumps(command, separators=(',', ':'), ensure_ascii=True).encode('ascii') + b'\n'
    if len(wire) > TARGET_PROTOCOL['maxWireBytes']:
        raise ValueError('Command is too long for the target input buffer (220 bytes maximum).')
    return command, wire


def _write_command(command, expected_epoch=None, confirmed=False):
    command, wire = _command_object(dict(command) if isinstance(command, dict) else command)
    safe = command == '?' or all(k in TARGET_PROTOCOL['safeCommands'] for k in command)
    if not safe and confirmed is not True:
        raise ValueError('Confirm this command before changing the target.')
    for key, value in ([] if command == '?' else command.items()):
        limits = TARGET_PROTOCOL['fields'].get(key)
        if limits and (not isinstance(value, (int, float)) or not limits['min'] <= value <= limits['max']
                       or limits['integer'] and int(value) != value):
            raise ValueError('Value out of range for ' + key)
    with lock:
        if not state['connected'] or state['resource'] is None:
            raise ValueError('Connect to the target before sending a command. Commands are not queued for reconnect.')
        epoch = state['connection_epoch']
        if expected_epoch is not None and expected_epoch != epoch:
            raise ValueError('The target connection changed. Get Settings again before writing.')
        resource, generation = state['resource'], state['generation']
        method = (state['config'] or {}).get('method', 'tcp')
    try:
        if method == 'tcp':
            resource.sendall(wire)
        else:
            position = 0
            while position < len(wire):
                written = resource.write(wire[position:])
                if not written:
                    raise OSError('USB write timed out')
                position += written
        with lock:
            if generation != state['generation'] or epoch != state['connection_epoch']:
                raise OSError('Connection changed while writing')
    except OSError as exc:
        push(dict(type='error', message='Command write failed; it may have been partially sent. Get Settings before retrying: ' + str(exc)), generation)
        raise OSError('Command write failed; no automatic retry was performed. Get Settings before retrying.') from exc
    logged = '?' if command == '?' else {k: ('********' if any(s in k.upper() for s in ('PWD', 'PASSWORD', 'SECRET')) else v) for k, v in command.items()}
    push(dict(type='sent', text=logged if isinstance(logged, str) else json.dumps(logged, separators=(',', ':')), transport=method), generation)
    return dict(sent=True, connection_epoch=epoch, generation=generation)


def send_command(command, expected_epoch=None, confirmed=False):
    with write_lock:
        return _write_command(command, expected_epoch, confirmed)


def _wait_settings(after, epoch, expected=None, timeout=25.0):
    deadline = time.monotonic() + timeout
    with settings_changed:
        while True:
            if not state['connected'] or state['connection_epoch'] != epoch:
                raise ValueError('Target disconnected. Get Settings again after reconnecting.')
            current = state['target_settings']
            if current and state['settings_event_id'] > after and all(
                    k in current and math.isclose(float(current[k]), float(v), rel_tol=1e-6, abs_tol=1e-6)
                    for k, v in (expected or {}).items()):
                return dict(settings=dict(current), connection_epoch=epoch,
                            generation=state['generation'], settings_event_id=state['settings_event_id'])
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ValueError('No complete settings response within 25 seconds. Check Arduino Terminal for the ECHO output; firmware sends settings slowly over Wi-Fi. No write will be retried automatically.')
            settings_changed.wait(remaining)


def get_target_settings():
    with write_lock:
        with lock:
            after, epoch = state['settings_event_id'], state['connection_epoch']
        _write_command('?', epoch)
        return _wait_settings(after, epoch)


def apply_target_settings(changes, expected_epoch, confirmed):
    if confirmed is not True:
        raise ValueError('Confirm the target settings changes first.')
    if not isinstance(changes, dict) or not changes:
        raise ValueError('No settings changes supplied.')
    with write_lock:
        with lock:
            current = dict(state['target_settings'] or {})
            epoch = state['connection_epoch']
        if expected_epoch != epoch or not current:
            raise ValueError('Get Settings from the current connection before applying changes.')
        for key, value in changes.items():
            if key not in TARGET_PROTOCOL['fields'] or key not in current:
                raise ValueError('Setting not supported by the current target: ' + key)
            limits = TARGET_PROTOCOL['fields'][key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not limits['min'] <= value <= limits['max'] or limits['integer'] and value != int(value):
                raise ValueError('Invalid value for ' + key)
        # Fit the AVR's 256-byte input buffer, and wait for a verified ECHO
        # between chunks instead of coalescing multiple JSON objects.
        chunks, chunk = [], {}
        for key, value in changes.items():
            candidate = dict(chunk, **{key: value})
            try:
                _command_object(dict(candidate, ECHO=0))
                chunk = candidate
            except ValueError:
                if not chunk:
                    raise
                chunks.append(chunk)
                chunk = {key: value}
        if chunk:
            chunks.append(chunk)
        result = None
        for chunk in chunks:
            with lock:
                after = state['settings_event_id']
            # The final ECHO is parsed as a separate field in the same Arduino
            # input object. The target may need >4 seconds to stream its reply.
            _write_command(dict(chunk, ECHO=0), epoch, confirmed=True)
            result = _wait_settings(after, epoch, chunk)
        return dict(result, verified=True)


def reject_constant(value):
    raise ValueError('Invalid JSON numeric constant: ' + value)


def parse_target_packet(raw):
    """Repair redundant separators outside strings, retaining literal string data."""
    try:
        return json.loads(raw, parse_constant=reject_constant)
    except json.JSONDecodeError:
        out, quoted, escaped, last = [], False, False, None
        for ch in raw:
            if quoted:
                out.append(ch)
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    quoted = False
                    last = '"'
            else:
                if ch == ',' and last == ',':
                    continue
                if ch == '"':
                    quoted = True
                out.append(ch)
                if not ch.isspace():
                    last = ch
        return json.loads(''.join(out), parse_constant=reject_constant)


class PacketStream:
    """Incremental JSON-object framing shared by USB and TCP, amid trace text."""
    def __init__(self, generation):
        self.generation = generation
        self.decoder = codecs.getincrementaldecoder('utf-8')('replace')
        self.buffer = ''

    def feed(self, data):
        with lock:
            if self.generation != state['generation']:
                return
            state['bytes_received'] += len(data)
        push(dict(type='raw', text=data.decode('utf-8', 'replace')[:3000], bytes=len(data)), self.generation)
        self.buffer += self.decoder.decode(data).replace('\x00', '')
        while True:
            start = self.buffer.find('{')
            if start < 0:
                self.buffer = ''
                return
            self.buffer = self.buffer[start:]
            depth, quoted, escaped, end = 0, False, False, None
            for i, ch in enumerate(self.buffer):
                if quoted:
                    if escaped:
                        escaped = False
                    elif ch == '\\':
                        escaped = True
                    elif ch == '"':
                        quoted = False
                elif ch == '"':
                    quoted = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end is None:
                if len(self.buffer) > 65536:
                    with lock:
                        if self.generation == state['generation']:
                            state['parse_errors'] += 1
                    push(dict(type='parse_error', text='Oversize incomplete packet discarded'), self.generation)
                    self.buffer = ''
                return
            raw, self.buffer = self.buffer[:end], self.buffer[end:]
            try:
                packet = parse_target_packet(raw)
            except (json.JSONDecodeError, ValueError):
                with lock:
                    if self.generation == state['generation']:
                        state['parse_errors'] += 1
                push(dict(type='parse_error', text=raw[:1000]), self.generation)
                continue
            with lock:
                if self.generation != state['generation']:
                    return
                state['raw_packets'] += 1
                method = (state['config'] or {}).get('method', 'tcp')
            if not isinstance(packet, dict):
                continue
            if 'shot' in packet:
                try:
                    miss = packet.get('miss', 0) in (True, 1, '1')
                    x = float(packet.get('x', 0) if miss else packet['x'])
                    y = float(packet.get('y', 0) if miss else packet['y'])
                    if not math.isfinite(x) or not math.isfinite(y):
                        raise ValueError('Nonfinite coordinates')
                    push(dict(type='shot', count=int(packet['shot']), x=x, y=y,
                              miss=miss, transport=method, raw=packet), self.generation)
                except (ValueError, TypeError, KeyError):
                    push(dict(type='message', data=packet), self.generation)
            else:
                push(dict(type='message', data=packet), self.generation)
                if 'NAME_ID' in packet and ('LED_BRIGHT' in packet or 'SENSOR' in packet) and 'PAPER_TIME' in packet:
                    with settings_changed:
                        if self.generation == state['generation']:
                            state['target_settings'] = dict(packet)
                            state['settings_event_id'] = state['next_id'] - 1
                            settings_changed.notify_all()


def serial_ports():
    if list_ports is None:
        return []
    return [dict(device=p.device, description=p.description, serial_number=p.serial_number,
                 vid=p.vid, pid=p.pid, location=p.location) for p in list_ports.comports()]


def choose_serial_port(config, identity):
    ports = serial_ports()
    if identity and identity.get('serial_number'):
        matches = [p for p in ports if all(p.get(k) == identity.get(k)
                   for k in ('serial_number', 'vid', 'pid'))]
        return matches[0]['device'] if len(matches) == 1 else None
    return config['serial_port']


def stop_connection():
    with lock:
        state['generation'] += 1
        cancel, resource = state['cancel'], state['resource']
        if cancel:
            cancel.set()
        state.update(connected=False, connecting=False, resource=None, cancel=None, target_settings=None, message='Disconnected')
        settings_changed.notify_all()
    if resource:
        try:
            if isinstance(resource, socket.socket):
                resource.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            resource.close()
        except OSError:
            pass
    push(dict(type='status', connected=False, message='Disconnected'))


def read_connection(config, generation, cancel, identity=None):
    resource = None
    while not cancel.is_set():
        try:
            if config['method'] == 'serial':
                port = choose_serial_port(config, identity)
                if port is None:
                    raise OSError('Waiting for the selected USB target')
                # Configure control lines before opening; drivers may still reset an Arduino.
                resource = serial.Serial(port=None, baudrate=config['baudrate'], timeout=0.25,
                                         write_timeout=1.0, bytesize=8, parity='N', stopbits=1,
                                         xonxoff=False, rtscts=False, dsrdtr=False)
                resource.dtr = False
                resource.rts = False
                resource.port = port
                resource.open()
                connected_config = dict(config, serial_port=port)
                matching = [p for p in serial_ports() if p['device'] == port]
                identity = matching[0] if len(matching) == 1 else identity
                message = f"USB connected · {port} @ {config['baudrate']}"
            else:
                resource = socket.create_connection((config['host'], config['port']), timeout=8)
                resource.settimeout(0.5)
                connected_config = config
                message = f"Wi-Fi/TCP connected · {config['host']}:{config['port']}"
            with lock:
                if generation != state['generation'] or cancel.is_set():
                    return
                state['connection_epoch'] += 1
                state['target_settings'] = None
                state.update(resource=resource, connected=True, connecting=False, message=message,
                             successful_config=connected_config, identity=identity)
            push(dict(type='status', connected=True, message=message), generation)
            stream = PacketStream(generation)
            while not cancel.is_set():
                if config['method'] == 'serial':
                    data = resource.read(min(max(resource.in_waiting, 1), 4096))
                    if not data:  # Normal read timeout, not a serial disconnect.
                        continue
                else:
                    try:
                        data = resource.recv(4096)
                    except socket.timeout:
                        continue
                    if not data:
                        raise OSError('Target closed the TCP connection')
                stream.feed(data)
        except (OSError, ValueError) as exc:
            if cancel.is_set():
                return
            retry = config['method'] == 'serial' and config.get('auto_reconnect', True)
            message = (f'USB disconnected · retrying: {exc}' if retry else f'Connection failed: {exc}')
            with lock:
                if generation != state['generation']:
                    return
                state.update(connected=False, connecting=retry, resource=None, message=message)
            push(dict(type='error', message=message), generation)
            if not retry:
                return
        finally:
            if resource:
                try:
                    resource.close()
                except OSError:
                    pass
                resource = None
        if cancel.wait(1.5):
            return


def validate_config(obj):
    if not isinstance(obj, dict):
        raise ValueError('Invalid connection settings')
    method = obj.get('method', 'tcp')
    if method == 'serial':
        port = str(obj.get('serial_port', '')).strip()
        if not port or len(port) > 250 or not (re.fullmatch(r'COM[1-9][0-9]*', port, re.I)
                or port.startswith(('/dev/cu.', '/dev/tty.', '/dev/ttyUSB', '/dev/ttyACM', '/dev/serial/'))):
            raise ValueError('Select or enter a local serial port, e.g. COM3 or /dev/cu.usbserial...')
        baud = int(obj.get('baudrate', 115200))
        if not 300 <= baud <= 2000000:
            raise ValueError('Enter a baud rate between 300 and 2000000')
        if serial is None:
            raise ValueError('USB support needs pySerial. Run INSTALL_USB_SUPPORT.bat (Windows) or INSTALL_USB_SUPPORT.command (macOS), then restart the bridge.')
        return dict(method='serial', serial_port=port, baudrate=baud,
                    auto_reconnect=obj.get('auto_reconnect', True) is not False)
    if method != 'tcp':
        raise ValueError('Unknown connection method')
    host, port = str(obj.get('host', '')).strip(), int(obj.get('port', 1090))
    if not host or not 1 <= port <= 65535 or any(c in host for c in '/\\ \n\r\t'):
        raise ValueError('Invalid TCP host/port')
    return dict(method='tcp', host=host, port=port)


def start_connection(config):
    with lock:
        if state['connected'] or state['connecting']:
            raise ValueError('Already connected or reconnecting. Disconnect first to change methods.')
        state['generation'] += 1
        generation, cancel = state['generation'], threading.Event()
        state.update(config=config, cancel=cancel, connected=False, connecting=True, identity=None,
                     message='Connecting…', bytes_received=0, raw_packets=0, parse_errors=0)
    threading.Thread(target=read_connection, args=(config, generation, cancel), daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, obj, status=200):
        data = json.dumps(obj, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == '/api/events':
            try:
                after = int(parse_qs(p.query).get('after', ['0'])[0])
            except ValueError:
                after = 0
            with lock:
                self.respond({**{k: state[k] for k in ('connected', 'connecting', 'message',
                    'bytes_received', 'raw_packets', 'parse_errors', 'successful_config', 'connection_epoch')},
                    'method': (state['config'] or {}).get('method', 'tcp'),
                    'events': [e for e in state['events'] if e['id'] > after], 'latest': state['next_id'] - 1})
        elif p.path == '/api/serial-ports':
            try:
                self.respond(dict(available=serial is not None, ports=serial_ports()))
            except OSError as exc:
                self.respond(dict(available=serial is not None, ports=[], error=str(exc)))
        elif p.path in ('/', '/index.html'):
            try:
                data = (ROOT / 'freETarget_Live_v1.6.html').read_bytes()
            except FileNotFoundError:
                return self.respond(dict(error='Extract the entire ZIP into one folder.'), 500)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)
        else:
            self.respond(dict(error='Not found'), 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path in ('/api/command', '/api/get-target-settings', '/api/target-settings'):
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 1 <= size <= 4096:
                    raise ValueError('Invalid command request size')
                obj = json.loads(self.rfile.read(size), parse_constant=reject_constant)
                if not isinstance(obj, dict):
                    raise ValueError('Invalid command request')
                if path == '/api/command':
                    result = send_command(obj.get('command'), obj.get('connection_epoch'), obj.get('confirmed') is True)
                elif path == '/api/get-target-settings':
                    result = get_target_settings()
                else:
                    result = apply_target_settings(obj.get('changes'), obj.get('connection_epoch'), obj.get('confirmed') is True)
                return self.respond(result)
            except (ValueError, TypeError) as exc:
                return self.respond(dict(error=str(exc)), 400)
            except OSError as exc:
                return self.respond(dict(error=str(exc)), 502)
        if path == '/api/disconnect':
            stop_connection()
            return self.respond(dict(ok=True))
        if path == '/api/clear-diagnostics':
            with lock:
                # Preserve all shot events: clearing a log must not lose unpolled shots.
                state['events'] = [e for e in state['events'] if e['type'] == 'shot']
                state.update(bytes_received=0, raw_packets=0, parse_errors=0)
                latest = state['next_id'] - 1
            return self.respond(dict(ok=True, latest=latest))
        if path != '/api/connect':
            return self.respond(dict(error='Not found'), 404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= 4096:
                raise ValueError('Invalid request size')
            config = validate_config(json.loads(self.rfile.read(size)))
            start_connection(config)
            self.respond(dict(ok=True))
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.respond(dict(error=str(exc)), 400)


if __name__ == '__main__':
    print('freETarget v1.7.9 at http://127.0.0.1:8765')
    if serial is None:
        print('Wi-Fi/TCP ready. USB is optional: run INSTALL_USB_SUPPORT to add pySerial.')
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
