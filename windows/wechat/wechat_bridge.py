#!/usr/bin/env python3
"""Windows drop-in replacement for WeFlow's HTTP API (native reader, no Electron).

Serves the endpoints the harness uses, with WeFlow's JSON shapes + Bearer auth, backed by
wechat_db_win (direct SQLCipher-4 decrypt). Point WEFLOW_BASE at this and retire WeFlow.exe.

  GET /health                              -> {"status":"ok"}
  GET /api/v1/sessions?limit=N             -> {"success":true,"sessions":[...]}
  GET /api/v1/messages?talker=X&limit=N    -> {"success":true,"count":N,"messages":[...]}

Run:  set WECHAT_BRIDGE_TOKEN=<tok> && python wechat_bridge.py --port 5031
"""
import argparse, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wechat_db_win as wechat_db  # noqa: E402

TOKEN = os.environ.get("WECHAT_BRIDGE_TOKEN", "")


class Handler(BaseHTTPRequestHandler):
    def _auth_ok(self):
        if not TOKEN:
            return True
        return self.headers.get("Authorization", "") == f"Bearer {TOKEN}"

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            return self._json({"status": "ok"})
        if not self._auth_ok():
            return self._json({"error": "unauthorized"}, 401)
        q = parse_qs(u.query)
        try:
            if u.path == "/api/v1/sessions":
                limit = int(q.get("limit", ["2000"])[0])
                return self._json({"success": True, "sessions": wechat_db.sessions(limit=limit)})
            if u.path == "/api/v1/messages":
                talker = q.get("talker", [""])[0]
                if not talker:
                    return self._json({"error": "talker required"}, 400)
                limit = int(q.get("limit", ["200"])[0])
                msgs = wechat_db.messages(talker, limit=limit)
                return self._json({"success": True, "talker": talker, "count": len(msgs),
                                   "hasMore": False, "messages": msgs})
            if u.path.startswith("/api/v1/media/"):
                return self._json({"error": "media not yet wired"}, 501)
            return self._json({"error": "not found"}, 404)
        except Exception as e:
            return self._json({"error": str(e)}, 500)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5031)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"wechat-bridge(win) on http://{a.host}:{a.port}  token={'set' if TOKEN else 'OFF'}", file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
