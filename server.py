#!/usr/bin/env python3
"""LogMind web server (standard library only). Run: python server.py [port]"""
import json, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from analyzer import analyze
from generate_sample import generate

ROOT = Path(__file__).parent
MAX_BYTES = 50 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/sample":
            self._send(200, json.dumps(analyze(generate())).encode(), "application/json")
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        size = int(self.headers.get("Content-Length", 0))
        if self.path != "/api/analyze" or size > MAX_BYTES:
            return self._send(400, b"Bad request", "text/plain")
        text = self.rfile.read(size).decode("utf-8", errors="replace")
        self._send(200, json.dumps(analyze(text)).encode(), "application/json")

    def log_message(self, fmt, *args):
        print("  ", fmt % args)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    url = f"http://localhost:{port}"
    print(f"LogMind running at {url}  (Ctrl+C to stop)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
