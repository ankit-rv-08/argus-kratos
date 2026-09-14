"""Argus API and static web server."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from inference import analyze_context
from tools import build_dossier, build_dossier_stream

ROOT = Path(__file__).parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, payload: dict[str, object]) -> None:
        self._send(200, json.dumps(payload).encode(), "application/json")

    def do_GET(self) -> None:
        request = urlparse(self.path)
        path = request.path
        if path == "/api/health":
            self._send(200, b'{"status":"ok","service":"argus"}', "application/json")
            return
        if path == "/api/dossier":
            ticker = parse_qs(request.query).get("ticker", ["NVDA"])[0]
            self._json(build_dossier(ticker))
            return
        if path == "/api/stream":
            ticker = parse_qs(request.query).get("ticker", ["NVDA"])[0].upper()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            for event in build_dossier_stream(ticker):
                self.wfile.write(f"data: {json.dumps(event)}\n\n".encode())
                self.wfile.flush()
            return
        if path == "/api/inference":
            self._json(analyze_context("NVIDIA data center revenue hit records, but new export restrictions threaten APAC growth."))
            return
        asset = ROOT / "web" / ("index.html" if path == "/" else path.removeprefix("/"))
        if asset.is_file() and asset.parent == ROOT / "web":
            content_type = "text/css" if asset.suffix == ".css" else "application/javascript" if asset.suffix == ".js" else "text/html"
            self._send(200, asset.read_bytes(), content_type)
            return
        self._send(404, b"Not found", "text/plain")

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8080), Handler)
    print("Argus listening at http://127.0.0.1:8080")
    server.serve_forever()
