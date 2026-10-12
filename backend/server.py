from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes


HOST = "0.0.0.0"
PORT = 8080

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/get_some_data":
            self.send_json(
                {
                    "message": "Hello world!"
                }
            )
            return

        self.serve_frontend()

    def do_POST(self):
        self.handle_api_request()

    def do_PUT(self):
        self.handle_api_request()

    def do_DELETE(self):
        self.handle_api_request()

    def handle_api_request(self):
        if self.path != "/get_some_data":
            self.send_error(404, "Endpoint not found")
            return

        self.send_json(
            {
                "message": "Hello world!",
                "method": self.command
            }
        )

    def serve_frontend(self):
        request_path = self.path.split("?", 1)[0]

        if request_path == "/":
            file_path = FRONTEND_DIR / "index.html"
        else:
            relative_path = request_path.lstrip("/")
            file_path = FRONTEND_DIR / relative_path

        try:
            file_path = file_path.resolve()
            frontend_root = FRONTEND_DIR.resolve()

            if frontend_root not in file_path.parents and file_path != frontend_root:
                self.send_error(403, "Forbidden")
                return

            if not file_path.is_file():
                self.send_error(404, "File not found")
                return

            content = file_path.read_bytes()
            content_type, _ = mimetypes.guess_type(file_path.name)

            self.send_response(200)
            self.send_header("Content-Type", content_type or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        except OSError:
            self.send_error(500, "Could not read file")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler)
    print(f"Server started: http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
