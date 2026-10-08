#!/usr/bin/env python3
"""Dependency-free HTTP API for the Yemeni Legal Assistant."""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from retrieval.engine import LegalRetriever, answer_context
from reasoning.legal_reasoner import build_reasoning
from drafting.legal_drafter import draft

ROOT = Path(__file__).resolve().parents[1]
retriever = LegalRetriever(ROOT)
INDEXED_CHUNKS = retriever.build()

class Handler(BaseHTTPRequestHandler):
    server_version = "YemeniLegalAssistant/1.0"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {
                "status": "ok",
                "service": "yemeni-legal-assistant",
                "indexed_chunks": INDEXED_CHUNKS,
            })
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/query":
            self._send(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                self._send(413, {"error": "request_too_large"})
                return
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": "invalid_json"})
            return

        question = str(payload.get("question", "")).strip()
        if not question:
            self._send(400, {"error": "question_required"})
            return

        limit = max(1, min(int(payload.get("limit", 8)), 20))
        facts = payload.get("facts", [])
        if not isinstance(facts, list):
            facts = [str(facts)]
        requested_relief = payload.get("requested_relief")
        mode = str(payload.get("mode", "legal_answer"))

        results = retriever.search(question, limit=limit)
        context = answer_context(results)
        reasoning = build_reasoning(
            question,
            results,
            facts=[str(x) for x in facts],
            requested_relief=str(requested_relief) if requested_relief else None,
        )

        self._send(200, {
            "service": "yemeni-legal-assistant",
            "version": "1.0",
            "question": question,
            "retrieval": {
                "indexed_chunks": INDEXED_CHUNKS,
                "count": len(results),
                "sources": context["sources"],
                "context": context["context"],
            },
            "reasoning": reasoning,\n            "drafting": drafting,
            "notice": "هذه الطبقة تسترجع المصادر وتنظم الاستدلال ولا تغني عن التحقق من المصدر الرسمي والنفاذ والتعديلات.",
        })

    def log_message(self, format: str, *args) -> None:
        return

def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Yemeni Legal Assistant API listening on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
