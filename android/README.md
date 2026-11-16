# freETarget Minimalist Android 0.2.2-beta.1 (version code 4)

Android source preview based on the iPhone and iPad 0.2.5 scoring interface. The Android app talks directly to the target via Wi-Fi/TCP or USB serial and stores profiles, guns, history and settings on the device.

## Build and install

1. Clone or download this repository and open its `android/` folder in Android Studio.
2. The build declares JDK 17, Android SDK Platform 35, Android Gradle Plugin 8.7.3, and Android 11 or later (minSdk 30). The package's build instructions specify Gradle 8.9, but the committed wrapper currently requests Gradle 9.9.0. That configuration discrepancy still needs to be resolved before treating wrapper builds as verified.
3. Select a connected Android 11 or later phone or tablet and click **Run**. For a sideloadable debug APK, use **Build APK(s)** or run `gradle :app:assembleDebug` from the project directory with Gradle 8.9 installed. The file is written to `app/build/outputs/apk/debug/app-debug.apk`.

## Mobile layout

Phones request portrait and use the top Dashboard and bottom icon navigation. Tablets use a left sidebar, may rotate, and remember widget sizes separately in portrait and landscape. On phones the top bar includes Play/Pause, Next Stage and Log. Pinch on the main target to zoom, then drag with one finger to pan. The target overlays fade after shots if enabled in Settings → Appearance. Tablets fit Previous Target to its content in landscape. The target connection settings offer Station and Access Point modes USB serial, and connection diagnostics. The optional prompt to start a session after a detected shot is under **Settings → General**. Accepting the prompt carries that shot to the target and scores it only if the opening stage accepts shots.

## First connection

1. Join the same Wi-Fi network as the freETarget. To use target access-point mode, join the target’s Wi-Fi network directly.
2. Open **Settings → Connection**. For Station mode enter the target IP and TCP port, usually **1090**. Access Point mode uses **192.168.10.9:1090**.
3. Save, then tap **Connect Target**. Confirm the status turns green and scores arrive. Log a session under a named shooter, then reopen the app to check History. Check that unplugging or turning off the target leaves a clear disconnected status.

## USB serial

1. Connect the target with a data-capable USB cable. Use a USB OTG adapter if needed. The Android phone or tablet must support USB host mode.
2. Choose **Settings → Connection → USB / Serial**, refresh the list, select the target, and save. The baud rate defaults to **115200**, with 8 data bits, no parity, and one stop bit.
3. Tap **Connect Target** and approve Android’s USB permission prompt if shown. After unplugging or reconnecting the cable, refresh the list if the previously saved port is unavailable.

The build uses [usb-serial-for-android](https://github.com/mik3y/usb-serial-for-android) and resolves it from JitPack on the first Gradle sync.

## Beta scope

- The app disconnects when it leaves the foreground. Reconnect when you return.
- The preview focuses on receiving live scores over Wi-Fi and USB. Target settings editing, the Arduino terminal, custom logo uploads, and Files backup import/export are outside this preview.
- Profiles and logged results stay on the installed device. Uninstalling or clearing app data removes them.
- The JavaScript adapter and shared mobile interface were checked locally. An Android Studio build and phone/tablet layout, audio, and physical-device Wi-Fi and USB tests are pending. Keep Android System WebView up to date. This repository contains source; no signed Android release APK is currently published under [GitHub Releases](https://github.com/DaveStruve/freETarget-Minimalist-Desktop/releases).

## Credits

Based on the original [freETarget project](https://github.com/ten-point-nine/freETarget), the [freETarget Minimalist adaptation](https://free-e-target.com/freeetarget-minimalist/), and freETarget Minimalist Desktop. Upstream and third-party notices are included.
