#!/usr/bin/env python3
"""HTTP API entry point for the Yemeni Legal Assistant."""
from __future__ import annotations
import hmac, json, os, ipaddress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from retrieval.hybrid import HybridRetriever
from retrieval.engine import answer_context
from verification.verifier import verify
from reasoning.legal_reasoner import build_reasoning
from drafting.legal_drafter import draft
from cases.case_engine import analyze_case

ROOT = Path(__file__).resolve().parents[1]
retriever = HybridRetriever(ROOT)
INDEXED_CHUNKS = retriever.build()
MAX_BODY_BYTES = 1_000_000

def _is_loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == "localhost"

class Handler(BaseHTTPRequestHandler):
    server_version = "YemeniLegalAssistant/1.3"
    sys_version = ""

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        key = os.getenv("API_KEY", "").strip()
        client_ip = self.client_address[0] if self.client_address else ""
        if key:
            supplied = self.headers.get("Authorization", "")
            expected = "Bearer " + key
            return hmac.compare_digest(supplied, expected)
        # A missing key is acceptable only for loopback development.
        return _is_loopback(client_ip)

    def do_GET(self):
        if self.path != "/health":
            return self._send(404, {"error": "not_found"})
        return self._send(200, {
            "status": "ok", "service": "yemeni-legal-assistant",
            "version": "1.4", "indexed_chunks": INDEXED_CHUNKS,
            "mode": "local-development" if not os.getenv("API_KEY") else "authenticated"
        })

    def do_POST(self):
        if self.path not in ("/query", "/case"):
            return self._send(404, {"error": "not_found"})
        if not self._authorized():
            return self._send(401, {"error": "unauthorized", "message": "استخدم ترويسة Authorization: Bearer <API_KEY>."})
        try:
            raw_length = self.headers.get("Content-Length", "0")
            length = int(raw_length)
            if length < 0:
                return self._send(400, {"error": "invalid_content_length"})
            if length > MAX_BODY_BYTES:
                return self._send(413, {"error": "request_too_large"})
            raw = self.rfile.read(length)
            payload = json.loads(raw or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "invalid_json"})
        if not isinstance(payload, dict):
            return self._send(400, {"error": "json_object_required"})
        try:
            if self.path == "/case":
                return self._send(200, {"case_analysis": analyze_case(payload)})
            question = payload.get("question")
            if not isinstance(question, str) or not question.strip():
                return self._send(400, {"error": "question_required"})
            try:
                limit = int(payload.get("limit", 8))
            except (TypeError, ValueError):
                return self._send(400, {"error": "limit_must_be_integer"})
            if not 1 <= limit <= 20:
                return self._send(400, {"error": "limit_out_of_range", "allowed": "1..20"})
            facts = payload.get("facts", [])
            facts = facts if isinstance(facts, list) else [facts]
            facts = [str(x)[:10_000] for x in facts[:100]]
            requested_relief = payload.get("requested_relief")
            requested_relief = str(requested_relief)[:10_000] if requested_relief is not None else None
            mode = str(payload.get("mode", "legal_answer"))
            # Refresh on every query so newly edited local project materials are included.
            # The API reads the checked-out repository; sync/pull is required to obtain new GitHub commits.
            global INDEXED_CHUNKS
            INDEXED_CHUNKS = retriever.build()
            results = retriever.search_hybrid(question.strip()[:20_000], limit)
            context = answer_context(results)
            verification = verify(results)
            reasoning = build_reasoning(question.strip(), results, facts, requested_relief)
            drafting = draft(
                {"question": question.strip(), "facts": facts, "requested_relief": requested_relief},
                reasoning, mode
            )
            return self._send(200, {
                "service": "yemeni-legal-assistant", "version": "1.4",
                "question": question.strip(),
                "retrieval": {"indexed_chunks": INDEXED_CHUNKS, "count": len(results),
                              "sources": context["sources"], "context": context["context"]},
                "verification": verification, "reasoning": reasoning, "drafting": drafting,
                "notice": "نظام استرجاع وتحليل أولي؛ لا تعتمد مسودة قانونية قبل مراجعة المصدر الرسمي والنفاذ والوقائع."
            })
        except Exception:
            # Do not leak request contents, paths, or stack traces to API clients.
            return self._send(500, {"error": "internal_error", "message": "تعذر إكمال الطلب؛ راجع سجلات التشغيل المحلية."})

    def log_message(self, *args):
        return

def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    if not _is_loopback(host) and not os.getenv("API_KEY", "").strip():
        raise SystemExit("Refusing non-loopback bind without API_KEY. Set API_KEY or use HOST=127.0.0.1.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()
