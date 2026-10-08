import json
import os
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.app import Handler

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
    finally:
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    test_health_endpoint()
    print("OK")
