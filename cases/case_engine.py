#!/usr/bin/env python3
"""Structured Yemeni case analysis engine."""
from __future__ import annotations
from typing import Any

SECTIONS = ("facts","evidence","defenses","applicable_law","violations","requests")

def analyze_case(case: dict[str, Any]) -> dict[str, Any]:
    result = {k: case.get(k, []) for k in SECTIONS}
    facts, evidence, laws, violations = result["facts"], result["evidence"], result["applicable_law"], result["violations"]
    gaps = []
    if not facts: gaps.append("لا توجد وقائع مدخلة.")
    if not evidence: gaps.append("لا توجد أدلة مدخلة.")
    if not laws: gaps.append("لم تحدد نصوص قانونية منطبقة.")
    if not violations: gaps.append("لم تحدد أوجه المخالفة أو عناصر الجريمة/الدفع.")
    links = [{"law": law, "supporting_facts": facts, "supporting_evidence": evidence, "alleged_violation": violations} for law in laws]
    return {"case_summary": result, "legal_links": links, "gaps": gaps, "ready_for_drafting": not gaps}
