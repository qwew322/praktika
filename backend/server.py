from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import json
import mimetypes

import controller
import database

HOST = "0.0.0.0"
PORT = 8080
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, body, content_type):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self._send_response(status_code, body, "application/json; charset=utf-8")

    def _serve_static(self, request_path):
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
        content_type = content_type or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript", "application/json"
        }:
            content_type += "; charset=utf-8"

        self._send_response(200, file_path.read_bytes(), content_type)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b""
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))

    def _run_controller(self, handler, *args):
        try:
            status, payload = handler(*args)
        except (ValueError, LookupError) as error:
            status, payload = 400, {"error": str(error)}
        self._send_json(status, payload)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)

        if path.startswith("/static/"):
            self._serve_static(path)
        elif path == "/":
                    html = (BASE_DIR / "static" / "index.html").read_bytes()
                    self._send_response(200, html, "text/html; charset=utf-8")
        elif path == "/test_api":
            html = (BASE_DIR / "test_api.html").read_bytes()
            self._send_response(200, html, "text/html; charset=utf-8")
        elif path == "/category":
            self._run_controller(controller.get_categories, params)
        elif path == "/article":
            self._run_controller(controller.get_articles, params)
        elif path == "/some_data":
            self._send_json(200, {"message": "Hello world!", "params": params})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        self._handle_body_request({
            "/category": controller.post_category,
            "/article": controller.post_article,
        })

    def do_PUT(self):
        self._handle_body_request({
            "/category": controller.put_category,
            "/article": controller.put_article,
        })

    def _handle_body_request(self, routes):
        path = urlparse(self.path).path
        handler = routes.get(path)
        if handler is None:
            self._send_json(404, {"error": "Not found"})
            return

        try:
            body = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON"})
            return

        self._run_controller(handler, body)

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)

        routes = {
            "/delete_category": controller.delete_category,
            "/delete_article": controller.delete_article,
        }
        handler = routes.get(path)
        if handler is None:
            self._send_json(404, {"error": "Not found"})
            return

        self._run_controller(handler, params)

    def log_message(self, format, *args):
        print(
            f"[{self.log_date_time_string()}] "
            f"{self.client_address[0]} - {format % args}"
        )


if __name__ == "__main__":
    database.init_database()
    server = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Server started: http://localhost:{PORT}")
    print(f"API Tester: http://localhost:{PORT}/test_api")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
