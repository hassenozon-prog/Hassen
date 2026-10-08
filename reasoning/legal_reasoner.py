#!/usr/bin/env python3
"""Deterministic legal reasoning layer for retrieved Yemeni sources."""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class LegalIssue:
    question: str
    facts: list[str]
    requested_relief: str | None = None

def extract_legal_numbers(text: str) -> dict[str, list[str]]:
    return {
        "articles": sorted(set(re.findall(r"(?:المادة|مادة)\s*(\d+)", text))),
        "laws": sorted(set(re.findall(r"(?:قانون|القانون)\s*(?:رقم\s*)?(\d+)\s*(?:لسنة|لعام)\s*(\d{3,4})?", text))),
        "cases": sorted(set(re.findall(r"(?:القضية|الطعن|الدعوى)\s*(?:رقم\s*)?([\d/]+)", text))),
    }

def classify_issue(question: str) -> str:
    q = question.lower()
    if any(x in q for x in ["المداولة", "دليل لم يطرح", "دليل لم يقدم", "الجلسة"]):
        return "trial_evidence_and_deliberation"
    if any(x in q for x in ["منازعة تنفيذ", "التنفيذ", "الحجز التنفيذي"]):
        return "execution_dispute"
    if any(x in q for x in ["نقض", "طعن", "بطلان الحكم", "قصور في التسبيب"]):
        return "cassation"
    if any(x in q for x in ["ملكية", "حيازة", "عقار", "تعدي"]):
        return "property"
    return "general"

def source_strength(source: dict[str, Any]) -> float:
    status = source.get("verification_status")
    effective = source.get("effective_status")
    score = float(source.get("score", 0))
    if status == "verified":
        score += 0.20
    if status == "needs-verification":
        score -= 0.15
    if effective == "current":
        score += 0.15
    if effective == "superseded":
        score -= 0.30
    return score

def build_reasoning(question: str, results: list[dict[str, Any]], facts: list[str] | None = None,
                    requested_relief: str | None = None) -> dict[str, Any]:
    facts = facts or []
    issue = LegalIssue(question, facts, requested_relief)
    ranked = sorted(results, key=source_strength, reverse=True)
    issue_type = classify_issue(question)

    supported = [r for r in ranked if r.get("verification_status") == "verified"
                 and r.get("effective_status") != "superseded"]
    uncertain = [r for r in ranked if r not in supported]

    propositions = []
    for r in supported:
        propositions.append({
            "proposition": r.get("title") or r.get("path"),
            "support": r.get("citation") or r.get("path"),
            "text": r.get("text", ""),
        })

    warnings = []
    if uncertain:
        warnings.append("بعض النتائج تحتاج إلى تحقق إضافي قبل اعتمادها كمرجع نهائي.")
    if not supported:
        warnings.append("لم تتوفر نتيجة موثقة نافذة تكفي وحدها لحسم المسألة.")

    return {
        "issue": asdict(issue),
        "issue_type": issue_type,
        "legal_numbers": extract_legal_numbers(question),
        "supported_sources": supported,
        "uncertain_sources": uncertain,
        "propositions": propositions,
        "warnings": warnings,
        "drafting_instruction": (
            "ميّز بين النص القانوني الثابت والوقائع والاستنتاج. "
            "لا تنسب مبدأً للمحكمة العليا إلا إذا كان مصدره موثقاً."
        ),
    }

def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("question")
    p.add_argument("--results-json", help="JSON file containing retrieval results")
    args = p.parse_args()
    results = []
    if args.results_json:
        with open(args.results_json, encoding="utf-8") as f:
            payload = json.load(f)
        results = payload.get("results", [])
    print(json.dumps(build_reasoning(args.question, results), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
