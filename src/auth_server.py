import http.server
import socketserver
import urllib.parse
import threading
from src.logger import logger

class AuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/callback":
            query = urllib.parse.parse_qs(parsed_path.query)
            code = query.get('code', [None])[0]

            if code:
                self.server.auth_code = code
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Login Successful!</h1><p>You can close this window and return to the application.</p>")
            else:
                self.send_response(400)
                self.wfile.write(b"<h1>Error: No code found</h1>")
        else:
            self.send_response(404)
            self.end_headers()

class AuthServer:
    def __init__(self, port=5000):
        self.port = port
        self.server = None
        self.thread = None
        self.auth_code = None

    def start_server(self):
        handler = AuthHandler
        self.server = socketserver.TCPServer(("127.0.0.1", self.port), handler)
        self.server.auth_code = None

        logger.info(f"Auth Server started on port {self.port}")
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def wait_for_code(self, timeout=60):
        import time
        start = time.time()
        while time.time() - start < timeout:
            if getattr(self.server, 'auth_code', None):
                code = self.server.auth_code
                self.stop_server()
                return code
            time.sleep(0.5)
        self.stop_server()
        return None

    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Auth Server stopped")
