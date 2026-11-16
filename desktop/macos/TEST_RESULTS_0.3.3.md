# freETarget Minimalist 0.3.3 — QA Results

**Execution environment:** Linux, Python 3.13, Node.js 22, headless Chromium. Real target hardware and native Windows/macOS environments were not available for acceptance testing.

## Automated suites

- Windows: 46 Python unittest tests passed. Node.js UI/scoring, five-shot, statistics, desktop bootstrap, migration exporter, and storage validation passed.
- macOS: 56 Python unittest tests passed. Same Node.js suites, plus the iOS adapter regression suite, passed.
- Both platform scripts parsed successfully as JavaScript.

## Headless Chromium acceptance

- Existing 0.3.3 navigation and session selectors, statistics chart layout, independent demo data, saved sessions, and pause-on-leave passed.
- Six widget definitions and the approved Small/Large restrictions verified.
- Default visibility: original four widgets visible, Scorecard and Session Details available to add.
- Customization controls: add/remove, size toggle, up/down ordering, drag/drop between visible cards, saved layout persistence across reload, reset.
- Two small widgets in the same row have matching heights.
- Previous Target scales to the full widget width at a 1:1 aspect ratio, without clipping.
- Scorecard updates with 12 simulated demo shots, shows series totals, group/centre, and selecting a series displays its target.
- Session Details shows structure, sighters, 15-minute sighting stage, 75-minute record stage, and progress milestones.
- New Session Details labels render in Simplified Chinese when selected.
- No JavaScript page errors in tested flows.

## Remaining beta verification

- Build and run on native Windows/macOS.
- Verify live Wi-Fi/USB target shots, pauses, LED behavior, and audio latency on hardware.
- Verify long-duration sessions and specialized rules, including five-shot and finals, on real hardware.
- Review specialized translated labels with native-speaking shooters.
