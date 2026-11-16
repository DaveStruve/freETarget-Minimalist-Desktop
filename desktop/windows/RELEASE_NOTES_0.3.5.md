# freETarget Minimalist — Beta 0.3.5

**Platforms:** Windows 10/11 x64 and macOS (source packages with local build scripts)  
**Based on:** 0.3.4-beta.1  
**Compatibility:** freETarget Minimalist via USB/Serial or Wi-Fi/TCP  
**Data schema:** v1, unchanged; existing profiles, sessions, guns, and dashboard layouts remain in place

## Changes

1. **Labeled Edit Widgets button.** The gear icon in the bottom toolbar now includes the visible text **Edit Widgets**, immediately to the left of the Light/Dark Mode button. Editing behavior and accessibility state are retained. The text is localized for the app's supported languages.
2. **Session Details and Scorecard are collapsible.** Both panels now use the same header toggle as Live Scoring, Recent Shots, Shot Distribution, and Previous Target. Their independent expanded/collapsed preferences persist between launches and remain intact if a widget is hidden and shown again. A collapsed panel displays only its header. All future dashboard widgets inherit this shared collapse behavior.
3. **Consistent widget padding.** Session Details and Scorecard use the same card inset, header padding, and body padding as the existing widgets. The Session Details clock blocks stack in its Small layout to avoid timestamp overlap at narrow widths.
4. **Session Details streamlined.** Removed **Shooter**, **Gun**, and **Gun Type** from this widget only. The widget retains **Session**, **Structure**, timing, current stage, progress, and series indicators. Shooter/gun selection, profile records, session metadata, and saved session history are unchanged.

## Build / installation

- **Windows:** Extract the Windows source ZIP. Run `START_DESKTOP.bat` from source or `BUILD_WINDOWS.bat` to build. The optional installer build requires Inno Setup.
- **macOS:** Extract the macOS source ZIP. Run `START_MAC.command` from source or `BUILD_MAC.command` to build. The iOS/iPadOS preview is unchanged.

**These are source archives, not precompiled Windows/macOS installers.** Back up saved profiles and session history before upgrading.

## Validation

- Windows and macOS Python unit tests, Node.js UI/scoring/statistics/desktop-storage suites, and JS syntax checks.
- Chromium UI acceptance on both platforms at 1550×960, 1280×800, and 1000×750, including button placement, edit-mode toggle, collapse/expand and persisted preferences, widget padding, removed fields, and localization.
- Native Windows/macOS builds and real target hardware reception were **not** tested in this environment.
