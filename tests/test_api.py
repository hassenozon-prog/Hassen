import json
import os
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.app import Handler

def request_json(url, payload, headers=None):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))

def test_health_endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = "http://127.0.0.1:%d/health" % server.server_port
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
        assert data["status"] == "ok"
        assert data["indexed_chunks"] >= 1
        status, bad_limit = request_json("http://127.0.0.1:%d/query" % server.server_port, {"question": "test", "limit": "oops"})
        assert status == 400 and bad_limit["error"] == "limit_must_be_integer"
        status, non_object = request_json("http://127.0.0.1:%d/query" % server.server_port, ["not", "object"])
        assert status == 400 and non_object["error"] == "json_object_required"
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    test_health_endpoint()
    print("OK")
