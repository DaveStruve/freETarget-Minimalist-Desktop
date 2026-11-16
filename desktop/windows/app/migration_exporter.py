"""Readonly exporter UI at the original web app's browser origin."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from pathlib import Path
import webbrowser


def create_export_server(html_path, port=8765):
    html = Path(html_path).read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            allowed = {'127.0.0.1:' + str(self.server.server_address[1]), 'localhost:' + str(self.server.server_address[1])}
            if self.headers.get('Host') not in allowed:
                self.send_error(403)
                return
            if urlsplit(self.path).path != '/':
                self.send_error(404)
                return
            self.send_response(200)
            for name, value in [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(html))),
                                ('Cache-Control', 'no-store'), ('X-Frame-Options', 'DENY'), ('Referrer-Policy', 'no-referrer'),
                                ('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")]:
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(html)
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    return server


if __name__ == '__main__':
    server = create_export_server(Path(__file__).parent / 'assets/browser_export.html')
    print('Open http://127.0.0.1:8765/ in the ORIGINAL browser/profile. Ctrl+C stops this exporter.')
    webbrowser.open('http://127.0.0.1:8765/')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
