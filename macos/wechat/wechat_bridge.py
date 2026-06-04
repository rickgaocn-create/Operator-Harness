#!/usr/bin/env python3
"""Drop-in localhost replacement for WeFlow's HTTP API.

Serves exactly the three endpoints daily-wechat-ingest uses, with the same Bearer-token auth and
JSON shapes — so the harness works unchanged: just point WEFLOW_BASE at this bridge.

  GET /api/v1/sessions?limit=N            -> {"sessions":[{username,name,lastTimestamp}]}
  GET /api/v1/messages?talker=X&limit=N   -> {"messages":[{content,createTime,senderUsername,mediaType}]}
  GET /api/v1/media/<...>                  -> raw decrypted media bytes  (TODO: wire to image decryptor)

Run:  WECHAT_BRIDGE_TOKEN=<token> python3 wechat_bridge.py --port 5031
Then: export WEFLOW_BASE=http://127.0.0.1:5031  WEFLOW_TOKEN=<token>   (ingest.py unchanged)

stdlib only. Read-only. ~200 lines vs a 184MB Electron app.
"""
import argparse, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wechat_db  # noqa: E402

TOKEN = os.environ.get("WECHAT_BRIDGE_TOKEN", "")


class Handler(BaseHTTPRequestHandler):
    def _auth_ok(self):
        if not TOKEN:
            return True  # no token configured -> open (localhost only); set one for parity
        return self.headers.get("Authorization", "") == f"Bearer {TOKEN}"

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        if not self._auth_ok():
            return self._json({"error": "unauthorized"}, 401)
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path == "/api/v1/sessions":
                limit = int(q.get("limit", ["2000"])[0])
                return self._json({"sessions": wechat_db.sessions(limit=limit)})
            if u.path == "/api/v1/messages":
                talker = q.get("talker", [""])[0]
                limit = int(q.get("limit", ["200"])[0])
                if not talker:
                    return self._json({"error": "talker required"}, 400)
                return self._json({"messages": wechat_db.messages(talker, limit=limit)})
            if u.path.startswith("/api/v1/media/"):
                # TODO: map media id -> decrypted bytes via the image/voice decryptor (same key).
                return self._json({"error": "media not yet wired"}, 501)
            if u.path == "/api/v1/health":
                return self._json({"ok": True, "dbs": len(wechat_db.find_message_dbs())})
            return self._json({"error": "not found"}, 404)
        except Exception as e:
            return self._json({"error": str(e)}, 500)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5031)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"wechat-bridge on http://{a.host}:{a.port}  (token {'set' if TOKEN else 'OFF — localhost only'})",
          file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
