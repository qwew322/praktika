from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import json
import mimetypes

HOST = "0.0.0.0"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code: int, body: bytes, content_type: str) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send_response(status_code, body, "application/json; charset=utf-8")

    def _serve_static(self, request_path: str) -> None:
        relative_path = unquote(request_path.removeprefix("/static/"))
        file_path = (STATIC_DIR / relative_path).resolve()

        try:
            file_path.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self._send_json(403, {"error": "Forbidden"})
            return

        if not file_path.is_file():
            self._send_json(404, {"error": "Static file not found"})
            return

        content_type, _ = mimetypes.guess_type(file_path.name)
        if content_type is None:
            content_type = "application/octet-stream"

        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json"
        }:
            content_type += "; charset=utf-8"

        self._send_response(200, file_path.read_bytes(), content_type)

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        if path.startswith("/static/"):
            self._serve_static(path)
            return

        if path == "/test_api":
            html = (BASE_DIR / "index.html").read_bytes()
            self._send_response(200, html, "text/html; charset=utf-8")
            return


        if path == "/get_some_data":
            self._send_json(200, {
                "message": "Hello world!",
                "params": query_params
            })
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path != "/echo":
            self._send_json(404, {"error": "Not found"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b""

        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else None
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Request body must be valid JSON"})
            return

        self._send_json(200, {
            "message": "POST received",
            "params": query_params,
            "body": body
        })

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} - {format % args}")

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Server started: http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
