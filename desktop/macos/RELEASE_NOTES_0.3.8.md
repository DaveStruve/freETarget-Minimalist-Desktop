# freETarget Minimalist — 0.3.8-beta.1

## Sidebar and Previous Target refinements (Windows and macOS)

This update builds on **0.3.7-beta.1**. It changes presentation and control placement only; target communications, session scoring, profiles, saved history, and the storage schema remain unchanged.

1. **Redesigned expandable sidebar.** A compact teal chevron tab now protrudes from the sidebar's upper-right edge. The tab points left while expanded and right while collapsed. The sidebar has a rounded outer edge and subtle shadow. Expanded and collapsed widths animate smoothly, except when the system requests reduced motion. The existing navigation and session controls are preserved; no new example/mockup navigation pages were added.
2. **Fixed Connect Target button.** The Connect/Disconnect action is anchored at the bottom of the sidebar immediately **above the horizontal divider above Live Scoring**. Session setup controls scroll independently above it, so scrolling or resizing does not move the connection action. The full label is visible when expanded; the existing Plug/Unplug icon appears alone when collapsed. It still delegates to the same connection handler and follows the same enabled/disabled and connected/disconnected states.
3. **Previous Target selector centered.** The previous/next series arrows and series number are horizontally centered as a single group at the **top of the target image**, retaining the translucent theme-aware overlay and existing click behavior.
4. **Centered collapsed logo.** The built-in freETarget target icon is centered horizontally in the collapsed sidebar's header, with the full SVG logo restored when expanded. Accent, shot, and sidebar text colors remain live theme-aware. Custom uploaded logos remain supported and centered in the collapsed header.

### Additional compatibility notes

- A horizontal rule separates the logo/header from the session controls.
- The sidebar connection button remains anchored above the navigation at desktop and narrow viewport widths, including when the session controls are scrollable.
- The application retains the existing `ft-sidebar-collapsed` preference and the `ft-dashboard-widgets-v1` layout key. The storage schema is still **1**.
- The status bar now displays **freETarget Minimalist 0.3.8**.

## Source packages

- Windows: `freETarget_Minimalist_0.3.8-beta.1_Windows_Source.zip`
- macOS (Intel + Apple Silicon universal2): `freETarget_Minimalist_0.3.8-beta.1_macOS_Universal_Source.zip`

These ZIPs contain buildable **source**, not precompiled installers or signed native applications.

### Build on macOS

Unzip the macOS source package, open Terminal, and run:

```bash
cd "$HOME/Downloads/freETarget_Minimalist_0.3.8-beta.1_macOS_Universal"
bash BUILD_MAC.command
```

The universal2 build process writes `release/mac/freETarget Minimalist.app` and `release/mac/freETarget-Minimalist-0.3.8-beta.1-universal2.zip`. See `BUILD_UNIVERSAL_MAC.md` for universal Python and prerequisite setup. Native macOS builds, signing, and notarization must be performed on a Mac.

### Build on Windows

Unzip the Windows source package and run `BUILD_WINDOWS.bat`. To produce a Windows installer, run `BUILD_INSTALLER.bat` with Inno Setup 6 installed. The installer is written to `release\installer\`.

## Tests

- **Windows:** 71 Python unit tests passed; Node.js UI/scoring, desktop adapter, exporter, and storage tests passed.
- **macOS:** 88 Python unit tests passed, including universal2 build-selection checks; Node.js UI/scoring, iOS adapter, exporter, and storage tests passed.
- **Chromium UI checks:** Expanded/collapsed logo centering, chevron positioning, fixed connection button above navigation, independent scrolling, Previous Target selector centering, and responsive layout at **1440×900, 1100×700, and 800×650**. Light/Dark visual snapshots were inspected.
- **Not tested here:** Native Windows installer creation, native macOS `.app` compilation, Apple signing/notarization, and physical freETarget USB/Wi-Fi hardware connectivity.

**Before installing a beta update, back up saved shooter and session data.**
