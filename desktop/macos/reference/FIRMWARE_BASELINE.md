# Confirmed firmware baseline — freETarget Minimalist beta

**Developer confirmation:** The uploaded archive `freETarget_WiFi_LED_Pin13(1).zip` was identified by the developer as the **final firmware source running on their Arduino**. It was compared byte-for-byte with the firmware source ZIP already in the beta companion pack; **the files are identical**.

- Internal software version: `4.2.8 WiFi Test 1` (`freETarget.h`).
- Controller sketch: `source/freETarget/freETarget.ino` (Arduino Mega 2560 per included README).
- Hardware-specific LED PWM mapping: `#define LED_PWM 13` in `analog_io.h`.
- Station Wi-Fi handling includes `AT+CWDHCP_CUR=1,1`, SSID join/IP checks, and a TCP server on port **1090** in `esp-01.ino`.
- Package type: **Arduino source ZIP**; no compiled `.hex` or ESP-01 firmware image.
- SHA-256 of `firmware/freETarget_WiFi_LED_Pin13.zip`: `c64f189573ac67bb8662798c9d2bfdc9b146872ab00fbf7f5b78765487f83220`.

## What is confirmed, and what is not

The developer reports that their Arduino is running the final firmware and that their freETarget Minimalist hardware communicates successfully with the Windows desktop beta. The supplied source archive matches the earlier companion source archive exactly. This does **not** independently prove that a freshly compiled binary matches the exact bytes flashed on the board. Other controller revisions, LED wiring, ESP-01 AT firmware versions, or freETarget builds are **not validated**.

**Tester guidance:** Try the desktop beta with your current functioning target firmware first. Firmware flashing is optional and hardware-specific; verify your board, pin wiring, and rollback plan before uploading. Do not share network credentials or private target configuration.
