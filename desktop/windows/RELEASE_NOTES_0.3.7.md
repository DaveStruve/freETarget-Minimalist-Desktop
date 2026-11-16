# freETarget Minimalist — 0.3.7-beta.1

## Dashboard and appearance update — Windows and macOS

This release applies the nine requested UI improvements to the existing 0.3.6 codebase. The freETarget scoring engine, hardware protocols, session storage schema, saved shooter/gun records, and historical results are unchanged.

1. **Previous Target placeholder in Light Mode:** The placeholder uses the active theme's panel surface and text colors, instead of a fixed dark background. Dark Mode remains dark.
2. **New built-in freETarget logo:** The sidebar's built-in mark is a transparent inline SVG modeled on the approved concentric-ring/crosshair logo with a smaller off-center dot and bold wordmark. Both rings and the center dot use **Appearance → Accent color**; the off-center dot uses the active Light/Dark **Shot color**; the wordmark and crosshair ticks use the sidebar text color. All update live when Appearance colors or the theme change. Uploaded custom light/dark logos still override the built-in SVG; resetting a custom logo restores the built-in SVG.
3. **All six widgets on by default, in the requested order:** Live Scoring (**Large**), Recent Shots (**Small**), Shot Distribution (**Small**), Previous Target (**Small**), Session Details (**Small**), Scorecard (**Large**). New installations and **Reset Layout** use this order. Existing saved widget arrangements and visibility preferences remain unchanged when upgrading.
4. **Shot Distribution subtitle:** Removed “Entire session · whole-ring counts”. A zero-point-shot note appears only when such shots exist.
5. **Previous Target series changer:** Moved inside the target square at top left with compact arrows, current/total series indicator, and a theme-aware translucent background. Navigation is separate from the clickable target so the arrows do not open the enlargement view.
6. **Previous Target placeholder position:** “Complete 10 shots to see a target here.” (or the configured page size) now overlays the bottom center of the target until a complete series exists. Completed-series statistics remain beneath the square target.
7. **Session Details cleanup:** Removed the extra timing track and stage-status line beneath Remaining; Session Progress follows the timing boxes. Removed the status line beneath the series progress bars while retaining counts, segment bars, and series labels.
8. **Shot Distribution bar sizing:** Ten rows now distribute evenly through the chart's 200px height. Each bar fills its row, capped at **three times the row number font height**. Ring numbers and counts remain vertically centered with their bars.
9. **Connection button icon:** Replaced the Plug Zap icon with the standard **Plug** icon on Connect Target (including the collapsed sidebar). When connected, the icon switches to **Unplug** for the disconnect action. Connection behavior is unchanged.

## Platform packages

- **Windows source:** `freETarget_Minimalist_0.3.7-beta.1_Windows_Source.zip`
- **macOS universal2 source:** `freETarget_Minimalist_0.3.7-beta.1_macOS_Universal_Source.zip`

These are **source packages**, not precompiled `.exe` or `.app` binaries.

### macOS (Intel and Apple Silicon)

Extract the macOS ZIP and run in Terminal:

```bash
cd "$HOME/Downloads/freETarget_Minimalist_0.3.7-beta.1_macOS_Universal"
bash BUILD_MAC.command
```

The successful build writes `release/mac/freETarget Minimalist.app` and `release/mac/freETarget-Minimalist-0.3.7-beta.1-universal2.zip`. The build still requires a compatible **universal2 Python** and the existing packaging prerequisites. See `BUILD_UNIVERSAL_MAC.md` in the package. Developer ID signing/notarization are not included.

### Windows

Extract the Windows ZIP, run `BUILD_WINDOWS.bat`, then `BUILD_INSTALLER.bat` (requires Inno Setup 6). The installer is written to `release\installer\`.

## Compatibility and testing

- Data schema remains **1** and the widget layout storage key remains **`ft-dashboard-widgets-v1`**. User-saved layouts are respected.
- Windows: **67 Python unit tests passed**; Node.js UI/scoring, desktop adapter, exporter, and storage suites passed.
- macOS: **84 Python unit tests passed**, including portable universal2 packaging/selector tests; Node.js suites passed, including iOS adapter tests.
- Chromium UI checks: initial widget order/sizes/visibility and Previous Target placement at **1550×960, 1280×800, and 1000×750** on both HTML variants. Additional interactive tests passed for Light/Dark appearance, live accent/shot recoloring, custom-logo upload/reset, Edit Widgets/Reset Layout, preserved custom layouts, and Previous Target overlay navigation.
- **Not tested here:** Native Windows installer compilation, native macOS `.app`/WebKit build, signing/notarization, Intel/Apple Silicon physical-device operation, or a real target hardware connection. Verify those on destination machines before distributing.

**Recommendation:** Back up local shooter and session data before installing any beta update.
