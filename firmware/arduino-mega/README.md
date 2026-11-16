# freETarget Minimalist Arduino Mega firmware

This directory contains the **Arduino Mega 2560 firmware source** from the
published [Wi-Fi Fix / LED Pin 13 source archive](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/download/v0.3.10-beta.1/freETarget-Minimalist-Arduino-Mega-WiFi-Fix-LED-Pin13-Source.zip).

## Fixes and configuration

- Wi-Fi Station Mode initialization and connection-handling fixes, including IP/DHCP response parsing.
- Additional ESP-01 Wi-Fi communication, receive-buffer, and credential-handling fixes.
- Access Point Mode and TCP port 1090 support.
- LED PWM pin configured to **13** in `freETarget/analog_io.h`, not the original pin 5.

## Build and flash

Open [`freETarget/freETarget.ino`](freETarget/freETarget.ino) in Arduino IDE.
Select **Arduino Mega 2560**, verify the hardware wiring, then compile and upload.
This repository contains **source only**: no compiled HEX or hardware-test report is included.
See [original package notes](ORIGINAL_PACKAGE_README.txt).

## Provenance and licensing

The source was imported unchanged from the 80,513-byte archive that accompanies
[release v0.3.10-beta.1](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases/tag/v0.3.10-beta.1)
(SHA-256: `c64f189573ac67bb8662798c9d2bfdc9b146872ab00fbf7f5b78765487f83220`).
This firmware derives from the [original freETarget project](https://github.com/ten-point-nine/freETarget)
and the [freETarget Minimalist adaptation](https://github.com/stoeckli/freETarget).
Preserve upstream attribution; check upstream licensing separately before redistribution.
