import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import platform_support
from controller import DesktopController
from types import SimpleNamespace
from storage import DataStore

class ApplePreparationTests(unittest.TestCase):
    def test_mac_data_is_in_application_support(self):
        with patch.object(platform_support.sys,'platform','darwin'),patch.object(Path,'home',return_value=Path('/Users/tester')):
            self.assertEqual(str(platform_support.data_directory()),'/Users/tester/Library/Application Support/freETarget/DesktopBeta')

    def test_mac_open_folder_uses_argument_list_for_spaces(self):
        with tempfile.TemporaryDirectory(prefix='ft apple ') as folder:
            controller=DesktopController(DataStore(folder),SimpleNamespace(),ROOT/'app/assets')
            with patch('controller.sys.platform','darwin'),patch('controller.subprocess.run') as run:
                self.assertTrue(controller.open_data_folder()['opened'])
                run.assert_called_once_with(['open',folder],check=True)

    def test_platform_host_and_build_assets_exist(self):
        text=(ROOT/'app/desktop.py').read_text()
        self.assertIn("gui='cocoa' if sys.platform == 'darwin'",text)
        self.assertEqual((ROOT/'mac/freetarget.icns').read_bytes()[:4],b'icns')
        for name in ['START_MAC.command','BUILD_MAC.command','BUILD_MAC_NATIVE.command','PREPARE_IOS.command']:
            self.assertTrue(os.access(ROOT/name,os.X_OK))

    def test_mac_launcher_selects_installed_python_315(self):
        # The old launcher rejected a Mac with only Python 3.15 installed.
        with tempfile.TemporaryDirectory() as folder:
            executable=Path(folder)/'python3.15'
            executable.write_text('#!/bin/sh\nprintf "3.15\\n"\n')
            executable.chmod(0o755)
            env=dict(os.environ,PATH=folder+os.pathsep+os.environ['PATH'])
            result=subprocess.run(['bash','-c','source tools/select_python.sh; ft_select_python; echo "SELECTED:$FT_PYTHON_VERSION:$FT_PYTHON"'],
                                  cwd=ROOT,env=env,capture_output=True,text=True,check=True)
            self.assertIn('SELECTED:3.15:python3.15',result.stdout)

    def test_mac_launcher_and_python_tasks_allow_multiple_versions(self):
        task=(ROOT/'tools/mac_tasks.py').read_text()
        self.assertIn('(3, 15)',task)
        self.assertIn('.venv-mac%s-%d.%d',task)
        for name in ['START_MAC.command','BUILD_MAC.command','BUILD_MAC_NATIVE.command','PREPARE_IOS.command']:
            launcher=(ROOT/name).read_text()
            self.assertIn('ft_select_universal_python' if name == 'BUILD_MAC.command' else 'ft_select_python', launcher)
            self.assertNotIn('command -v python3.12',launcher)

    def test_xcode_sources_and_resources_have_consistent_references(self):
        text=(ROOT/'ios/freETargetIOS.xcodeproj/project.pbxproj').read_text()
        ids=re.findall(r'(?m)^([A-F0-9]{24}) = ',text)
        self.assertEqual(len(ids),len(set(ids)))
        all_refs=set(re.findall(r'\b[A-F0-9]{24}\b',text))
        self.assertEqual(all_refs,set(ids))
        for filename in re.findall(r'path="([^"\n]+\.swift)";',text):
            self.assertTrue((ROOT/'ios/freETargetIOS'/filename).is_file(),filename)
        ET.parse(ROOT/'ios/freETargetIOS.xcodeproj/xcshareddata/xcschemes/freETargetIOS.xcscheme')

    def test_local_network_and_no_background_firing_modes(self):
        info=plistlib.loads((ROOT/'ios/freETargetIOS/Info.plist').read_bytes())
        self.assertIn('Minimalist',info['NSLocalNetworkUsageDescription'])
        self.assertNotIn('UIBackgroundModes',info)
        self.assertFalse(info['UIApplicationSceneManifest']['UIApplicationSupportsMultipleScenes'])
        privacy=plistlib.loads((ROOT/'ios/freETargetIOS/PrivacyInfo.xcprivacy').read_bytes())
        self.assertFalse(privacy['NSPrivacyTracking'])

    def test_ios_preview_assets_remain_unchanged_in_desktop_only_release(self):
        import hashlib
        ios_html = (ROOT/'ios/freETargetIOS/Web/index.html').read_bytes()
        self.assertEqual(hashlib.sha256(ios_html).hexdigest(),
                         '46e89fdeeae684dd01b7d6244947bd5dadb78a8aee94096b8fe4069cfa7929b9')
        self.assertIn('freETarget Minimalist — 0.3.11 Beta', (ROOT/'app/assets/index.html').read_text())
        self.assertEqual((ROOT/'ios/freETargetIOS/Web/ios_bootstrap.js').read_bytes(),(ROOT/'ios/ios_bootstrap.js').read_bytes())
        self.assertEqual((ROOT/'ios/freETargetIOS/Web/mobile.css').read_bytes(),(ROOT/'ios/mobile.css').read_bytes())

    def test_ios_native_surface_rejects_unsupported_commands(self):
        text=(ROOT/'ios/freETargetIOS/WebHost.swift').read_text()
        self.assertIn('send(replyHandler,501',text)
        self.assertNotIn('target.send(',text)
        self.assertIn('frame.isMainFrame',text)
        self.assertIn('try self.prepareHTML()',text)
        self.assertIn('self.store.restore(stage.values,expected:stage.revision)',text)

    def test_icon_catalog_sizes_and_platform_targets(self):
        import struct
        folder=ROOT/'ios/freETargetIOS/Assets.xcassets/AppIcon.appiconset'
        catalog=json.loads((folder/'Contents.json').read_text())
        for icon in catalog['images']:
            pixels=int(float(icon['size'].split('x')[0])*int(icon['scale'][0]))
            data=(folder/icon['filename']).read_bytes()
            self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II',data[16:24]),(pixels,pixels))
        self.assertIn('16.0',(ROOT/'ios/freETargetIOS.xcodeproj/project.pbxproj').read_text())

if __name__=='__main__':unittest.main()
