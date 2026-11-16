"""Windows desktop host. The existing target bridge runs in-process."""
from __future__ import annotations
import argparse
import contextlib
import logging
from logging.handlers import RotatingFileHandler
import pathlib
import sys
import threading

from controller import DesktopController
from platform_support import InstanceLock, data_directory, resource_directory, show_error
from service import DesktopHTTPServer
from storage import DataStore, validate_storage
from version import APP_NAME, DISPLAY_VERSION
import freetarget_bridge as bridge


class CloseCoordinator:
    """Cancel the synchronous close event, then run JS/dialogs off the GUI thread."""
    def __init__(self, window):
        self.window = window
        self.allowed = False
        self.pending = False
        self._lock = threading.Lock()

    def request(self):
        with self._lock:
            if self.allowed:
                return True
            if self.pending:
                return False
            self.pending = True
        threading.Thread(target=self.run, daemon=True).start()
        return False

    def run(self):
        try:
            state = self.window.evaluate_js('typeof window.FTDesktopPrepareClose === "function" ? window.FTDesktopPrepareClose() : null')
            needs_confirmation = state is None or bool(state.get('unsaved') or state.get('active'))
            if needs_confirmation:
                message = ('This session has been stopped or paused. Its unlogged result will be lost.\n\n'
                           'Close without logging it? Cancel keeps the app open.') if state else 'Close freETarget Minimalist?'
                if not self.window.create_confirmation_dialog('Close freETarget Minimalist', message):
                    return
            self.allowed = True
            self.window.destroy()
        except Exception:
            logging.exception('Could not complete the close request')
            try:
                if self.window.create_confirmation_dialog('Close freETarget Minimalist', 'The interface did not respond. Unlogged shots may be lost. Close the app?'):
                    self.allowed = True
                    self.window.destroy()
            except Exception:
                logging.exception('Native close dialog failed')
        finally:
            with self._lock:
                self.pending = False


def configure_logging(directory):
    folder = directory / 'logs'
    folder.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(folder / 'desktop.log', maxBytes=1024 * 1024, backupCount=3, encoding='utf-8')
    handlers = [file_handler]
    if sys.stderr:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(level=logging.INFO, handlers=handlers, format='%(asctime)s %(levelname)s %(message)s', force=True)


def launch(directory):
    directory = pathlib.Path(directory)
    lock = InstanceLock(directory).acquire()
    server = controller = store = None
    try:
        configure_logging(directory)
        import webview
        store = DataStore(directory)
        validate_storage(store.snapshot()['storage'])
        controller = DesktopController(store, bridge, resource_directory())
        try:
            store.automatic_backup(daily=True)
        except OSError:
            logging.exception('Automatic startup backup could not be written')
            controller.backup_warning = 'The automatic backup could not be saved. Use Export Backup to choose another location.'
        server = DesktopHTTPServer(controller)
        thread = threading.Thread(target=server.serve_forever, name='freETarget-local-service', daemon=True)
        thread.start()
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('freETarget.Minimalist.Beta')
        webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
        webview.settings['ALLOW_FILE_URLS'] = False
        webview.settings['ALLOW_DOWNLOADS'] = False
        window = webview.create_window(APP_NAME + ' — ' + DISPLAY_VERSION, server.url, width=1366, height=900,
                                      min_size=(950, 650), maximized=True, confirm_close=False, text_select=True,
                                      background_color='#edf1f5', zoomable=False)
        controller.window, controller.webview = window, webview
        close = CloseCoordinator(window)
        window.events.closing += close.request
        logging.info('Starting %s; data folder: %s', DISPLAY_VERSION, directory)
        # Force modern WebView2. Do not fall back to the retired Internet Explorer renderer.
        webview.start(gui='edgechromium', debug=False, private_mode=False, storage_path=str(directory / 'webview'))
    finally:
        bridge.stop_connection()
        if controller:
            with contextlib.suppress(Exception):
                controller.stop()
        if server:
            server.shutdown()
            server.server_close()
        if store:
            try:
                store.automatic_backup()
                store.checkpoint()
            except Exception:
                logging.exception('Final backup/checkpoint failed; committed database data was retained')
        lock.release()


def main(argv=None):
    parser = argparse.ArgumentParser(description='freETarget Windows Desktop Beta')
    parser.add_argument('--data-dir', help='Developer override for an isolated data folder')
    parser.add_argument('--check-data', action='store_true', help='Check local data without opening the app')
    args = parser.parse_args(argv)
    directory = data_directory(args.data_dir)
    if args.check_data:
        with contextlib.ExitStack() as stack:
            instance = InstanceLock(directory).acquire()
            stack.callback(instance.release)
            state = DataStore(directory).snapshot()
            validate_storage(state['storage'])
            if sys.stdout:
                print('Local data is valid:', directory)
        return 0
    if sys.platform != 'win32':
        show_error('This desktop beta targets Windows 10/11 x64. Its storage and regression tests can run on other systems.')
        return 1
    try:
        launch(directory)
        return 0
    except Exception as exc:
        logging.exception('Desktop startup failed')
        show_error('freETarget Minimalist could not start.\n\n' + str(exc) + '\n\nData folder: ' + str(directory) +
                   '\nYour existing data was not reset. Check logs/desktop.log.\nWindows needs Microsoft Edge WebView2 Runtime and .NET Framework 4.8. See START_HERE.md.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
