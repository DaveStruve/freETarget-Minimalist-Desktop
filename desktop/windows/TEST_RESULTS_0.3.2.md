# freETarget Minimalist 0.3.2 — QA Results

**Execution environment:** Linux container, Python 3.13, Node.js 22, headless Chromium. Native Windows/macOS builds and live freETarget hardware were **not** available for verification.

## Automated tests

- Windows: 41 Python unittest cases passed; Node.js UI, statistics, five-shot timing, desktop bootstrap, migration exporter, and storage validation suites passed.
- macOS: 51 Python unittest cases passed; Node.js UI, statistics, five-shot timing, desktop bootstrap, migration exporter, iOS adapter (unchanged preview), and storage validation suites passed.
- Source scripts passed `node --check` for both desktop versions.

## Headless Chromium UI acceptance

Tested on both Windows and macOS desktop HTML with simulated local storage and recorded session fixtures:

- Statistics chart renders and a clicked point opens a read-only session in History.
- Statistics filtered session list opens the same History review; Back returns to Statistics.
- A chart point shared by two sessions opens a session chooser.
- History review displays shot placements, series navigation, session totals, and metadata while Live Scoring stays hidden and its state remains separate.
- Session Rules opens in a scrollable popup and closes via X/Escape.
- Target color Light/Dark values save independently and can be switched back.
- Separate Light/Dark logo uploads save independently; a single logo falls back for both; removing one preserves the other.
- Switching to Simplified Chinese and Hindi translates core UI labels; restoring English works.
- Spoken-score language can differ from application language.
- No browser JavaScript errors occurred in these acceptance scenarios.

## Outstanding beta validation

- Build and launch natively on Windows and macOS, including OS-installed enhanced voices, accessibility, and font fallback for Hindi/Chinese/Japanese.
- Connect to a real freETarget Minimalist via Wi-Fi/TCP and USB/Serial and confirm shot reception, stage timing, target LED controls, and voice latency.
- Review non-English competition terminology with native speakers before describing the translations as complete.
- macOS iOS/iPadOS preview is unchanged by 0.3.2.
