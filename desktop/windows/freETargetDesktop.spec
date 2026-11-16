# Run on Windows with Python matching the target architecture with PyInstaller 6.22.3.
from pathlib import Path
from PyInstaller.utils.hooks import collect_all
root = Path(SPECPATH)
web_datas, web_binaries, web_hidden = collect_all('webview')
a = Analysis([str(root / 'app/desktop.py')], pathex=[str(root / 'app')],
    binaries=web_binaries, datas=[(str(root / 'app/assets'), 'assets')] + web_datas,
    hiddenimports=web_hidden + ['serial.tools.list_ports', 'serial.tools.list_ports_windows', 'clr', 'pythonnet'],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'cefpython3', 'gi', 'tkinter'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='freETargetMinimalist', debug=False,
    bootloader_ignore_signals=False, strip=False, upx=False, console=False,
    version=str(root / 'installer/version_info.txt'), icon=str(root / 'app/assets/freetarget.ico'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='freETargetMinimalist')
