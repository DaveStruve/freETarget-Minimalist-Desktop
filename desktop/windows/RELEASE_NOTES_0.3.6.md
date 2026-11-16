# freETarget Minimalist — 0.3.6-beta.1

## Maintenance update (Windows and macOS)

This update fixes three reported UI problems in the 0.3.5 release without changing shot reception, scoring rules, shooter/gun records, or session history.

1. **Mac logo caption removed.** The obsolete “Designed for the freETarget Minimalist build” line under the sidebar logo has been removed, along with its unused caption styling. The old Windows-only description in the Mac Backup dialog was also replaced with neutral backup guidance.
2. **Previous Target sizing on first launch.** The widget now sizes to its square target immediately, instead of relying on collapsing and reopening it. The panel uses content-driven height, and a deferred measurement plus resize observation recalculates the target on first layout, dashboard changes, collapse/expand, window resize, and return to Live Scoring. The complete target and details remain inside the widget.
3. **Edit Widgets is visibly interactive.** Clicking the bottom toolbar action now changes **Edit Widgets** to **Done Editing**, highlights the active state, shows the widget arrangement toolbar, and scrolls the dashboard information column to the editing controls. Clicking again exits editing mode. Existing add/remove, resize, reorder, reset, and saved layout functions remain available. The button label is localized, including the active label.

## Compatibility

- **Windows:** Source with `BUILD_WINDOWS.bat` and `BUILD_INSTALLER.bat` for the Windows application and installer.
- **macOS:** Universal2 source with `BUILD_MAC.command`, using the previously corrected universal Python selector and test runner. The resulting `.app` and `-universal2.zip` are intended for Intel (x86_64) and Apple Silicon (arm64).
- **Data:** Same storage schema and existing `ft-dashboard-widgets-v1` layout key. Existing shooter profiles, saved guns, session history, widget layout, and collapse preferences remain compatible. Back up data before upgrading.

## Test summary

- Windows: **60 Python unit tests passed**.
- macOS: **77 Python unit tests passed**, including portable universal2 packaging tests.
- Both platforms: JavaScript UI/scoring/desktop storage suites passed; macOS iOS adapter suite passed.
- Chromium browser acceptance: 1550×960, 1280×800, and 1000×750 on both platform HTML variants. Checked first-load Previous Target square geometry, collapse/reopen, Small/Large layouts, resizing, simulated view return, Edit Widgets click/pressed state/visible controls, add/remove persistence, Spanish localization, and Mac caption removal.
- **Not verified:** A native Mac `.app` build or macOS WebKit interaction, actual Intel/Apple Silicon hardware testing, Windows native installer compilation, or physical freETarget target connection. Those must be verified on the destination computers.

## macOS universal build

Extract `freETarget_Minimalist_0.3.6-beta.1_macOS_Universal_Source.zip`, then run:

```bash
cd "$HOME/Downloads/freETarget_Minimalist_0.3.6-beta.1_macOS_Universal"
bash BUILD_MAC.command
```

Successful output is in `release/mac/`:

- `freETarget Minimalist.app`
- `freETarget-Minimalist-0.3.6-beta.1-universal2.zip`
- `BUILD_INFO.json`

See `BUILD_UNIVERSAL_MAC.md` inside the Mac source package for details and verification steps. Developer ID signing and notarization are not included.

## Windows installer build

Extract the Windows source, run `BUILD_WINDOWS.bat` first, then `BUILD_INSTALLER.bat` (Inno Setup 6 required). Output is in `release/installer/`.

These ZIPs are **source packages**, not precompiled applications or installers.
