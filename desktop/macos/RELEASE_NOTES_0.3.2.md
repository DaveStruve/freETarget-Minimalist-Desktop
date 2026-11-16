# freETarget Minimalist — Beta 0.3.2

**Platforms:** Windows and macOS desktop source packages  
**Target:** freETarget Minimalist electronic scoring target  
**Base UI:** freETarget v1.7.9 · **Data schema:** 1 (unchanged)

## What's new

1. **Fixed dashboard and target proportions.** Removed the 0.3.1 draggable divider, keyboard resizing, and saved column ratio. The square target once again sizes automatically within the fixed layout.
2. **History-only saved-session review.** Opening a saved session stays in History, with a read-only target, series navigation, recorded shot scores and clock positions, session metadata, and summary metrics. The active Live Scoring session is not replaced, paused, or modified by reviewing history.
3. **Session Rules popup.** The sidebar button (expanded or collapsed) opens a larger, scrollable rules dialog. Closing the dialog returns to the same workspace; it does not expand the sidebar.
4. **Clickable statistics.** Progress Over Time chart points and the filtered session list beneath the chart open their saved-session results in History. Back returns to Statistics with filters intact. When multiple sessions share the same chart position, a chooser lists those sessions.
5. **More legible series selector.** Saved-session target series controls use the dark-grey target-overlay background with high-contrast text.
6. **Independent target colors.** Appearance offers Light and Dark configurations for target background, shot markers, and active shot markers. Shared accent and session colors remain global. Older colors initialize both modes and are retained.
7. **Independent custom logos.** Appearance offers Light and Dark logo uploads, previews, and removal. One uploaded logo is used in both modes when the other is missing. Previously saved single logos remain available through a backward-compatible migration path.
8. **Voice improvements.** Voice settings expose installed voices matching the chosen spoken language, prioritize enhanced/natural voices where detectable, and add pitch selection alongside volume and speed. Voice quality and language availability depend on voices installed in Windows/macOS. Score announcements use localized clock-position phrasing. No cloud voice service or subscription is required.
9. **Dedicated Settings → Languages tab.** English (default), Spanish, German, French, Italian, Portuguese, Hindi, Simplified Chinese, Traditional Chinese, and Japanese. Choose application language, spoken-score language independently, and regional number/date formatting. A Restore English button is included. **No language icon** was added elsewhere in the interface.

## Language coverage and known limitations

The initial language packs cover primary navigation, scoring labels, common controls, appearance, voice, saved-session review, and statistics terminology. **Specialized competition rules, diagnostics, hardware messages, long explanatory text, and some dynamically constructed sentences still use English fallback.** These are initial beta translations, not professionally reviewed translations. For official competition rules, refer to the applicable authoritative rulebook.

The existing Five-Shot Standard **range-command audio recordings remain in English**; changing the spoken-score language does not translate those recordings. Natural voice availability and pronunciation depend on the operating system's installed text-to-speech voices. The target's firmware and its connection protocol are unchanged.

## Compatibility and upgrade

- Shooter profiles, multiple guns per shooter, recorded shot data, session history, scoring rules, connection preferences, and previous logos are retained in the existing desktop data folder. **Data schema stays at version 1.**
- Existing target colors are copied into both appearance modes until changed separately. Existing single-logo data is read for both modes until separate logo preferences are saved.
- Export a backup from **Settings → Backup** before upgrading, especially during beta testing.
- The Mac package still includes the older **iOS/iPadOS preview** as a separate experimental project; this release's new features apply to Windows and macOS desktop, not the iOS preview.

## Build and test

- **Windows:** Extract the Windows source ZIP, then run `BUILD_WINDOWS.bat` on Windows. The optional installer script requires Inno Setup.
- **macOS:** Extract the macOS source ZIP, then run `BUILD_MAC.command` on a Mac with the required Python/build tools.
- Both packages are **source + local build scripts, not precompiled executable installers**. Native Windows/macOS builds and live freETarget hardware need to be tested on the respective platforms.
- Linux-based Python/Node regression suites and headless Chromium simulated-target UI checks passed for both desktop sources. See `TEST_RESULTS_0.3.2.md` inside each ZIP.
