# Attribution and build notices

Independent software designed for the freETarget Minimalist build. This is not an official freETarget release or a third-party endorsement.

- Upstream freETarget / ten-point-nine project and target protocol: https://github.com/ten-point-nine/freETarget . Its MIT notice is preserved in `licenses/freETarget-MIT.txt`.
- pywebview, pySerial and Python.NET notices from the desktop baseline are retained. macOS uses pywebview, pySerial, Python and PyObjC; Python.NET is not an iOS dependency. Installed Mac dependency metadata/notices are collected during a Mac build.
- The Python 3.12 interpreter notice is included in `licenses/Python-3.12-LICENSE.txt` from the upstream 3.12 branch. Mac Python/runtime builds retain their applicable notices. No Python runtime is bundled in the iOS target.
- The existing embedded synthetic command WAVs were generated using CMU Flite / SLT. Its COPYING text and the baseline audio provenance are preserved. The iOS project includes those WAVs as part of the shared HTML; it does not bundle the Flite executable or voice model.
- Native iOS code uses Apple's system SwiftUI, WebKit, Network, CryptoKit, UIKit and SQLite interfaces. The source package includes no Apple SDK, signing certificate, team credentials or proprietary runtime installer.
- The optional reference firmware source is unchanged from the user-confirmed archive. Its upstream attribution and hardware-specific limits remain in the accompanying reference notes.

Existing components retain their terms. This package does not grant a new blanket license over the original project. Review the exact built runtime/SDK notices and signing/distribution requirements before broader publication. No Windows installer is included in this Apple source package.
