#!/usr/bin/env python3
"""Урок 06. Loopback-only HTTP probe; deliberately returns 200, 503 and 404."""
from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        routes = {
            '/health': (200, {'status': 'ok', 'component': 'http'}),
            '/dependency': (503, {'status': 'unavailable', 'component': 'synthetic-db'}),
        }
        status, payload = routes.get(self.path, (404, {'error': 'not_found'}))
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return  # No user information or access logs.


@contextmanager
def local_server():
    # Ephemeral OS-assigned port, loopback only; no external network exposure.
    server = ThreadingHTTPServer(('127.0.0.1', 0), DemoHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def probe(url: str) -> tuple[int | None, dict[str, object] | str]:
    try:
        with urlopen(url, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode('utf-8'))
    except URLError as exc:
        return None, str(exc.reason)


def run_demo() -> dict[str, int]:
    results: dict[str, int] = {}
    with local_server() as port:
        for endpoint in ('/health', '/dependency', '/missing'):
            status, payload = probe(f'http://127.0.0.1:{port}{endpoint}')
            print(f'GET {endpoint:<12} → HTTP {status}: {json.dumps(payload, ensure_ascii=False)}')
            if status is None:
                raise RuntimeError(f'Cannot reach local endpoint {endpoint}')
            results[endpoint] = status
    expected = {'/health': 200, '/dependency': 503, '/missing': 404}
    if results != expected:
        raise AssertionError(f'Expected {expected}, observed {results}')
    print('PASS: три ожидаемых HTTP-ответа подтверждены; сервер завершён.')
    return results


if __name__ == '__main__':
    run_demo()
