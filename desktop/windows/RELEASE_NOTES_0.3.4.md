# freETarget Minimalist — Beta 0.3.4

**Platforms:** Windows 10/11 x64 and macOS (source packages with build scripts)  
**Based on:** 0.3.3-beta.1  
**Compatibility:** Designed for freETarget Minimalist, USB/Serial and Wi-Fi/TCP connections  
**Data schema:** v1, unchanged; existing desktop data folder and saved widget layouts retained

## Changes

1. **Customize Dashboard moved to the bottom toolbar.** The compact gear button now sits immediately to the left of the Light/Dark appearance toggle. Hover for its label, or activate it with the keyboard. It enters or exits the existing dashboard customization mode; all widget arrangement, visibility, size, and persistence controls remain available. The button is only displayed on the Live Scoring screen.
2. **Removed the dashboard's bottom fade.** The old sticky Customize Dashboard dock and its gradient background have been removed. Widgets now scroll without a fade covering their lower edges.
3. **Restored the original Dashboard/Target column proportions.** The width cap introduced in 0.3.3 for small widgets has been removed. The fixed layout from before the widget redesign is restored, and the main target SVG uses all available space in its square target panel. The target stays proportional and uncropped, and no draggable column divider is introduced. On narrower desktop windows, the widgets may be narrower and continue to stack as needed.
4. **Removed the Ready text below Log Score & End.** The redundant sidebar status line is hidden, with its spacing removed. Internal session state, scoring behavior, and the bottom status bar remain unchanged.

No shooter profiles, gun records, logged sessions, scoring rules, or saved dashboard widget layouts are migrated or deleted in this release.

## Install / build

- **Windows:** Extract the Windows source ZIP and use `START_DESKTOP.bat` to run from source or `BUILD_WINDOWS.bat` to build. `BUILD_INSTALLER.bat` requires Inno Setup.
- **macOS:** Extract the macOS source ZIP and use `START_MAC.command` to run or `BUILD_MAC.command` to build. The iOS/iPadOS preview is unchanged.

**These are source archives, not precompiled installers.** Export a backup of shooter profiles and session history before upgrading.

## Testing

- Windows and macOS Python unit suites, Node.js UI/scoring/statistics/desktop-storage suites, and JavaScript syntax checks.
- Chromium UI acceptance at 1550×960, 1280×800, and 1000×750 for both source variants: verified footer icon placement and behavior, target square sizing, restored width, removal of the fade and Ready line, and navigation visibility.
- Native Windows/macOS builds and live freETarget hardware have **not** been tested in this environment.
