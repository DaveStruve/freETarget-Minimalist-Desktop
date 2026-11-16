# freETarget Minimalist — 0.3.3 Beta 1

**Platforms:** Windows 10/11 x64 and macOS (source distributions)  
**Base UI:** freETarget Live v1.7.9 TEST  
**Hardware compatibility:** Designed for freETarget Minimalist; TCP/Wi-Fi and USB/Serial transport retained  
**Data schema:** v1 (unchanged); existing desktop data folder retained

## What's new

### 1. Customizable Live Scoring information column

The information column beside the main target now supports a configurable grid of six independent widgets. Use **Customize Dashboard** at the bottom of the column to enter editing mode, drag widgets to rearrange them, or use the up/down buttons for precise ordering. Use **Add / Remove Widgets** to show or hide panels; choose **Reset Layout** to restore the initial arrangement. Settings are stored locally and included in normal desktop backups. The main target stays outside the widget grid and remains square. The dashboard/target split is fixed, not draggable; the available width is balanced to keep widgets readable. On narrow windows, small widgets stack rather than clip.

| Widget | Permitted size(s) | Initially visible |
|---|---|---|
| Live Scoring | Small / Large | Yes |
| Recent Shots | Small only | Yes |
| Shot Distribution | Small / Large | Yes |
| Previous Target | Small / Large | Yes |
| Scorecard | Large only | No — add through Customize | 
| Session Details | Small only | No — add through Customize |

Small widgets take half the information-column width when there is room. Adjacent small widgets always have equal heights. The **Previous Target** shows the complete, square target at the widget's full available width without cropping; the series statistics sit below the target.

The new **Scorecard** widget includes sighters, numbered shot columns, series rows, series totals, X counts, total score, group diameter (maximum shot-to-shot spread), and mean centre offset. The active series is highlighted; selecting a scored series row displays that series on the main target. A new live shot returns the target to its current series. On narrow information columns the scorecard scrolls horizontally rather than reducing scores to unreadable sizes.

The new **Session Details** widget includes shooter, gun, gun type, session, session structure, elapsed time, remaining time (when timed), current stage, and a segmented shooting-progress indicator with sighters and series milestones. Timing follows the existing session engine, including pauses and independently timed stages.

### 2. History and Statistics navigation

- Removed redundant **Return to Live Scoring** and **Return to Session** buttons. Navigate via the main sidebar.
- Saved-session reviews remain in History; links from Statistics still open the same read-only History review and return to Statistics with its filters preserved.
- Optional **Settings → General → Pause Active Session When Leaving Live Scoring**, **off by default**. When enabled, navigating to History, Statistics, or Settings pauses the active session. Returning does not automatically resume it.

### 3. Sidebar controls

- Moved the Ready/session status below **Log Score & End**.
- Renamed **Shooter & Gun** to **Shooter** (selection of both shooter and gun is retained).
- Discipline and Session now use selection popups, with the chosen value displayed below each button title. The Session popup includes rules for the highlighted session, replacing the separate Session Rules sidebar button. Existing active-session selection locks are preserved.
- Applied consistent English heading capitalization; use **&** in concise labels where appropriate.

### 4. Statistics layout and filters

- The Progress over Time chart shares a row with its summary statistic cards; cards appear on the right at desktop widths and stack on narrow windows.
- Statistics filters are now **Exclude Sessions with Ignored Misses** and **Exclude Partial Sessions**. Both are **unchecked by default**, so all real sessions contribute unless excluded.

### 5. Isolated Demo Mode

- **Settings → General → Enable Demo Mode** switches to an independent sample dataset, including nine preloaded sessions and the ability to log additional simulated sessions.
- Demo Mode uses a separate demo shooter and history storage; real profiles, session history, averages, and personal bests remain unaffected.
- **Reset Demo Data** restores the original sample sessions after confirmation. Turning Demo Mode off does not delete its records.
- The former **Include Demo Sessions** Statistics checkbox has been removed because real and demo datasets are never mixed.
- Legacy demo sessions are copied into the demo dataset and migrated out of real History when migration succeeds. Back up before upgrading.

## Installation and upgrading

**Windows:** Extract the Windows source ZIP and use `START_DESKTOP.bat` to run from source or `BUILD_WINDOWS.bat` to compile on Windows. Optional `BUILD_INSTALLER.bat` builds an installer using Inno Setup.

**macOS:** Extract the macOS source ZIP and use `START_MAC.command` to run or `BUILD_MAC.command` to build on a Mac. The iOS/iPadOS preview remains unchanged.

These ZIP files contain **source code and build scripts**, not precompiled installers. The existing `DesktopBeta` data location is unchanged, but **export a complete backup before upgrading**, especially if you have older demo sessions.

## Validation completed

- Windows source: **46 Python unittest cases passed**, Node.js UI/scoring/statistics/five-shot/bootstrap/exporter/storage suites passed.
- macOS source: **56 Python unittest cases passed**, the same Node.js suites plus iOS adapter tests passed.
- Headless Chromium: tested modal selection, navigation, isolated demo dataset, pause-on-leave, statistics filters and chart layout, six-widget catalog, size restrictions, visibility, layout persistence, ordering, drag/drop, reset, equal-height small panels, full-width square Previous Target, scorecard updates with simulated shots, clickable series, Session Details stage timing, and new-widget Chinese translations. No JavaScript page errors in the tested flows.
- Both desktop sources passed JavaScript parsing checks.

**Not yet tested:** Native Windows/macOS builds, installed system voices, real freETarget hardware, long-running sessions, and the actual device transport/timing under live firing conditions. Browser-guided five-shot timing retains its existing limitations. Translations are still beta quality; some specialized text remains English.
