#!/usr/bin/env python3
"""HTTP API entry point for the Yemeni Legal Assistant."""
from __future__ import annotations
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from retrieval.hybrid import HybridRetriever
from retrieval.engine import answer_context
from verification.verifier import verify
from reasoning.legal_reasoner import build_reasoning
from drafting.legal_drafter import draft
from cases.case_engine import analyze_case

ROOT=Path(__file__).resolve().parents[1]
retriever=HybridRetriever(ROOT)
INDEXED_CHUNKS=retriever.build()

class Handler(BaseHTTPRequestHandler):
    server_version="YemeniLegalAssistant/1.2"
    def _send(self,status,payload):
        body=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=="/health":
            return self._send(200,{"status":"ok","service":"yemeni-legal-assistant","version":"1.2","indexed_chunks":INDEXED_CHUNKS})
        self._send(404,{"error":"not_found"})
    def do_POST(self):
        if self.path not in ("/query","/case"): return self._send(404,{"error":"not_found"})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>1_000_000: return self._send(413,{"error":"request_too_large"})
            payload=json.loads(self.rfile.read(length) or b"{}")
        except (ValueError,json.JSONDecodeError): return self._send(400,{"error":"invalid_json"})
        if self.path=="/case": return self._send(200,{"case_analysis":analyze_case(payload)})
        question=str(payload.get("question","")).strip()
        if not question: return self._send(400,{"error":"question_required"})
        limit=max(1,min(int(payload.get("limit",8)),20))
        results=retriever.search_hybrid(question,limit)
        context=answer_context(results); verification=verify(results)
        facts=payload.get("facts",[]); facts=facts if isinstance(facts,list) else [facts]
        reasoning=build_reasoning(question,results,[str(x) for x in facts],str(payload.get("requested_relief")) if payload.get("requested_relief") else None)
        drafting=draft({"question":question,"facts":[str(x) for x in facts],"requested_relief":payload.get("requested_relief")},reasoning,str(payload.get("mode","legal_answer")))
        return self._send(200,{"service":"yemeni-legal-assistant","version":"1.2","question":question,
          "retrieval":{"indexed_chunks":INDEXED_CHUNKS,"count":len(results),"sources":context["sources"],"context":context["context"]},
          "verification":verification,"reasoning":reasoning,"drafting":drafting})
    def log_message(self,*args): return

def main():
    ThreadingHTTPServer((os.getenv("HOST","127.0.0.1"),int(os.getenv("PORT","8080"))),Handler).serve_forever()
if __name__=="__main__": main()
