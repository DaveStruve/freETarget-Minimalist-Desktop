from __future__ import annotations
import ctypes
import logging
import os
import pathlib
import sys


def data_directory(override=None):
    if override:
        return pathlib.Path(override).expanduser().resolve()
    if sys.platform == 'win32':
        base = os.environ.get('LOCALAPPDATA')
        if not base:
            raise RuntimeError('Windows did not provide LOCALAPPDATA. No alternate data folder was created.')
        return pathlib.Path(base) / 'freETarget' / 'DesktopBeta'
    return pathlib.Path.home() / '.local' / 'share' / 'freETarget' / 'DesktopBeta'


def resource_directory():
    # __file__ points into PyInstaller's collected app directory when frozen.
    return pathlib.Path(__file__).resolve().parent / 'assets'


class InstanceLock:
    def __init__(self, directory):
        self.path = pathlib.Path(directory) / 'desktop.lock'
        self.file = None

    def acquire(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open('a+b')
        try:
            stream.seek(0, 2)
            if stream.tell() == 0:
                stream.write(b'0')
                stream.flush()
            stream.seek(0)
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            stream.close()
            raise RuntimeError('freETarget Minimalist is already running for this data folder. Close the existing app first.') from exc
        self.file = stream
        return self

    def release(self):
        if self.file:
            self.file.close()
            self.file = None


def show_error(message):
    logging.error('%s', message)
    if sys.platform == 'win32':
        ctypes.windll.user32.MessageBoxW(None, str(message), 'freETarget Minimalist', 0x10)
    elif sys.stderr:
        print(message, file=sys.stderr)
