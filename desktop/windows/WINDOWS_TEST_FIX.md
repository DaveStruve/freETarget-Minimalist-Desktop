# Windows SQLite test cleanup fix

The first Windows beta build reported 35 successful tests and two test cleanup errors (`WinError 32` for a temporary `freetarget.sqlite3`).

Cause: three direct `sqlite3.connect()` calls in `tests/test_storage.py` used the connection as a context manager. Python's SQLite connection context manager commits or rolls back but does not close the connection. Windows refuses to delete the temporary database while a handle is still open.

Fix: wrap those three test-only connections in `contextlib.closing()` and retain the SQLite transaction context so each connection is committed/rolled back and then closed before the temporary directory is removed.

The scoring app, bridge, user database format, and application code have not changed. This patch does not delete or modify any user data.

To apply to an already extracted source beta: replace only `tests\test_storage.py` with the supplied corrected file. Then run `BUILD_WINDOWS.bat` again. Alternatively, extract the full corrected source ZIP. You can keep your existing `.venv` directory; the build script may still verify/install its dependencies.

Windows execution remains to be confirmed on the user's machine.
