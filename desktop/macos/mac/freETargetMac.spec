from pathlib import Path
import os
from runpy import run_path
from PyInstaller.utils.hooks import collect_all
root = Path(SPECPATH).parent
release_version = run_path(str(root / 'app' / 'version.py'))['APP_VERSION'].split('-', 1)[0]
build_number = release_version.rsplit('.', 1)[-1]
datas, binaries, hidden = collect_all('webview')
identity = os.environ.get('FREETARGET_MAC_SIGN_IDENTITY') or None
a = Analysis([str(root/'app/desktop.py')], pathex=[str(root/'app')],
    binaries=binaries, datas=datas+[(str(root/'app/assets'),'assets'),(str(root/'licenses'),'licenses'),
                                   (str(root/'.build/mac-notices'),'licenses/installed'),(str(root/'START_HERE.txt'),'.')],
    hiddenimports=hidden+['serial.tools.list_ports_osx'],
    excludes=['PyQt5','PyQt6','PySide2','PySide6','cefpython3','gi','tkinter'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name='freETargetMinimalist',console=False,
    strip=False,upx=False,target_arch=os.environ.get('FREETARGET_MAC_ARCH'),
    codesign_identity=identity,entitlements_file=str(root/'mac/entitlements.plist') if identity else None)
coll = COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='freETargetMinimalist')
app = BUNDLE(coll,name='freETarget Minimalist.app',icon=str(root/'mac/freetarget.icns'),
    bundle_identifier='designs.struve.freetarget.desktop.preview',
    codesign_identity=identity,entitlements_file=str(root/'mac/entitlements.plist') if identity else None,
    info_plist={
        'CFBundleShortVersionString': release_version, 'CFBundleVersion': build_number,
        'LSMinimumSystemVersion':'13.0',
        'NSHighResolutionCapable':True,
        'NSLocalNetworkUsageDescription':'Connect to your freETarget Minimalist target on your local network to display shots.',
        'NSAppTransportSecurity':{'NSAllowsLocalNetworking':True}})
