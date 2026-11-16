"""Portable tests for the universal2 packaging path (no Mac binaries required)."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('ft_mac_tasks', ROOT / 'tools/mac_tasks.py')
mac_tasks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mac_tasks)


def fake_macho(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\xca\xfe\xba\xbe' + b'\x00' * 12)


class UniversalMacBuildTests(TestCase):
    def test_build_command_explicitly_requests_universal2(self):
        command = (ROOT / 'BUILD_MAC.command').read_text()
        spec = (ROOT / 'mac/freETargetMac.spec').read_text()
        self.assertIn('ft_select_universal_python', command)
        self.assertIn('FREETARGET_MAC_ARCH=universal2', command)
        self.assertIn("target_arch=os.environ.get('FREETARGET_MAC_ARCH')", spec)
        self.assertIn('ft_select_python', (ROOT / 'BUILD_MAC_NATIVE.command').read_text())

    def test_macho_detection_skips_regular_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'asset.json'
            path.write_text('{}')
            self.assertIsNone(mac_tasks.macho_arches(path))

    def test_bundle_verifier_checks_all_macho_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / 'freETarget Minimalist.app'
            exe = app / 'Contents/MacOS/freETargetMinimalist'
            lib = app / 'Contents/Frameworks/libpython.dylib'
            fake_macho(exe)
            fake_macho(lib)
            (app / 'Contents/Resources').mkdir(parents=True)
            (app / 'Contents/Resources/Info.plist').write_text('not macho')
            with patch.object(mac_tasks.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='arm64 x86_64', stderr='')) as run:
                self.assertEqual(mac_tasks.verify_universal_app(app), 2)
                self.assertGreaterEqual(run.call_count, 2)

    def test_bundle_verifier_rejects_missing_intel_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / 'freETarget Minimalist.app'
            exe = app / 'Contents/MacOS/freETargetMinimalist'
            fake_macho(exe)
            with patch.object(mac_tasks.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='arm64', stderr='')):
                with self.assertRaisesRegex(RuntimeError, 'requires arm64 and x86_64'):
                    mac_tasks.verify_universal_app(app)

    def test_bundle_verifier_rejects_missing_slices_in_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / 'freETarget Minimalist.app'
            exe = app / 'Contents/MacOS/freETargetMinimalist'
            lib = app / 'Contents/Frameworks/libexample.dylib'
            fake_macho(exe)
            fake_macho(lib)
            def run(args, **kwargs):
                return SimpleNamespace(returncode=0, stdout='arm64' if 'libexample' in args[-1] else 'arm64 x86_64', stderr='')
            with patch.object(mac_tasks.subprocess, 'run', side_effect=run):
                with self.assertRaisesRegex(RuntimeError, 'libexample.dylib'):
                    mac_tasks.verify_universal_app(app)

    def test_shell_python_selector_finds_two_slices_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            python = root / 'python3.13'
            python.write_text('#!/bin/sh\ncase "$*" in *sys.executable*) echo /fake/python3.13;; *) echo 3.13;; esac\n')
            python.chmod(0o755)
            lipo = root / 'lipo'
            lipo.write_text('#!/bin/sh\necho "arm64 x86_64"\n')
            lipo.chmod(0o755)
            # Force the synthetic interpreter. macOS may have a real
            # universal2 Python installed at an absolute framework path,
            # which must not override the fake interpreter used by this test.
            env = dict(os.environ, PATH=str(root) + os.pathsep + '/usr/bin:/bin',
                       FT_UNIVERSAL_PYTHON=str(python))
            result = subprocess.run(['bash', '-c', 'source tools/select_python.sh; ft_select_universal_python; echo "SELECTED:$FT_PYTHON_VERSION:$FT_PYTHON"'],
                                    cwd=ROOT, env=env, capture_output=True, text=True, check=True)
            self.assertIn('SELECTED:3.13:' + str(python), result.stdout)
            lipo.write_text('#!/bin/sh\necho "arm64"\n')
            result = subprocess.run(['bash', '-c', 'source tools/select_python.sh; ft_select_universal_python'],
                                    cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No universal2 Python found', result.stdout)

    @unittest.skipIf(sys.platform == 'darwin', 'Linux-only guard: invoking the macOS build here would recursively rerun the test suite')
    def test_mac_tasks_does_not_attempt_linux_build(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/mac_tasks.py'), 'build'],
                                cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('on macOS', result.stderr)
