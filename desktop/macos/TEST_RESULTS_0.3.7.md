# freETarget Minimalist 0.3.7-beta.1 — Test results

- Windows: 67/67 Python `unittest discover` tests passed.
- macOS: 84/84 Python `unittest discover` tests passed, including universal2 packaging tests.
- Windows `python tests/run_ui.py`: passed full JavaScript UI/scoring/desktop bootstrap/exporter/storage checks.
- macOS `python tests/run_ui.py`: passed the same checks plus iOS adapter checks.
- Headless Chromium checked 1550×960, 1280×800, and 1000×750 for both platform HTML variants. Default widget order and sizes, theme-aware SVG, previous-target overlay, placeholder position, ten distribution rows and bar heights were inspected.
- Interactive Chromium checks passed on both variants: Light/Dark appearance; live Accent and Dark Shot recoloring; custom logo upload/reset; dashboard Edit/Reset controls; preservation of preexisting saved widget layout; no lightbox activation from Previous Target navigation; no uncaught JavaScript errors.
- macOS build scripts were checked by portable unit tests. Native macOS universal2 app compilation and Windows installer compilation were **not** performed on Linux.
- Actual freETarget hardware connection, Apple WebKit interaction, and Intel/Apple Silicon native app testing remain to be done on the user's machines.
