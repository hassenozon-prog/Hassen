#!/usr/bin/env python3
"""Conservative Yemeni legal drafting layer.

Produces structured draft sections from verified retrieval/reasoning output.
It deliberately refuses to manufacture authorities, facts, or case numbers.
"""
from __future__ import annotations
from typing import Any
from verification.verifier import has_traceable_current_evidence

STYLE = {
    "cassation_ground": "سبب طعن بالنقض",
    "defense": "مذكرة دفاع",
    "prosecution_decision": "قرار نيابة",
    "judgment_reasons": "حيثيات وأسباب حكم",
    "legal_answer": "جواب قانوني",
}

def _source_line(source: dict[str, Any]) -> str:
    return source.get("citation") or source.get("path") or "مصدر غير محدد"

def draft(issue: dict[str, Any], reasoning: dict[str, Any], mode: str = "legal_answer") -> dict[str, Any]:
    mode = mode if mode in STYLE else "legal_answer"
    candidates = reasoning.get("supported_sources", [])
    supported = [s for s in candidates if isinstance(s, dict) and has_traceable_current_evidence(s)]
    warnings = list(reasoning.get("warnings", []))
    if candidates and not supported:
        warnings.append("رُفضت المصادر التي لا تحمل دليل تحقق قابلًا للتتبع وإثباتًا لحالة النفاذ الحالية.")
    question = issue.get("question", "")
    facts = issue.get("facts", [])
    if not supported:
        return {
            "mode": mode,
            "title": STYLE[mode],
            "status": "insufficient_verified_support",
            "draft": "",
            "warnings": warnings + ["لا يمكن إنشاء مسودة نهائية موثقة دون مصدر قانوني متحقق."],
        }

    source_lines = "\n".join(f"- {_source_line(s)}" for s in supported)
    fact_lines = "\n".join(f"- {f}" for f in facts) if facts else "- لم تُقدّم وقائع إضافية."

    opening = "وحيث إن" if mode in {"cassation_ground", "defense", "judgment_reasons"} else "ومن حيث إن"
    body = (
        f"{opening} المسألة المعروضة تتمثل في: {question}\n\n"
        "وحيث إن الوقائع المعتمدة في هذه المسودة هي الوقائع المقدمة فقط، دون إضافة وقائع غير ثابتة:\n"
        f"{fact_lines}\n\n"
        "وحيث إن المصادر القانونية المتحققة المستخرجة من قاعدة المعرفة هي:\n"
        f"{source_lines}\n\n"
        "ومن ثم، فإن التحليل النهائي يجب أن يربط كل واقعة بالنص المنطبق عليها، "
        "وأن يميز صراحةً بين النص القانوني وبين الاستنتاج القضائي، "
        "وألا ينسب إلى المحكمة العليا مبدأً غير موثق."
    )
    return {
        "mode": mode,
        "title": STYLE[mode],
        "status": "draft_ready_for_legal_review",
        "draft": body,
        "warnings": warnings,
        "sources": [_source_line(s) for s in supported],
    }
