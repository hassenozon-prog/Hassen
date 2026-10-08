#!/usr/bin/env python3
"""Lightweight retrieval engine for the Yemeni Legal Assistant."""
from __future__ import annotations
import json, re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
PUNCT = re.compile(r"[\W_]+", re.UNICODE)
STOPWORDS = {
    "من","في","على","عن","إلى","الى","أن","ان","إن","هو","هي","هذا","هذه",
    "ذلك","تلك","و","أو","او","ثم","مع","لا","ما","لم","لن","قد","كان","يكون",
    "به","بها","له","لها","لهم","كما","أي","أيضا","ايضا"
}

@dataclass
class Chunk:
    path: str
    title: str
    text: str
    source_type: str
    verification_status: str
    effective_status: str
    article: str | None = None
    law_number: str | None = None
    year: str | None = None

    def citation(self) -> str:
        parts = [self.path]
        if self.law_number:
            parts.append(f"قانون {self.law_number}")
        if self.article:
            parts.append(f"مادة {self.article}")
        return " — ".join(parts)

def normalize_arabic(text: str) -> str:
    text = text.lower()
    text = ARABIC_DIACRITICS.sub("", text)
    text = text.replace("أ","ا").replace("إ","ا").replace("آ","ا")
    text = text.replace("ى","ي").replace("ة","ه")
    text = text.replace("ؤ","و").replace("ئ","ي")
    return text

def tokens(text: str) -> set[str]:
    raw = PUNCT.sub(" ", normalize_arabic(text)).split()
    return {t for t in raw if len(t) > 1 and t not in STOPWORDS}

def yaml_scalar(content: str, key: str) -> str | None:
    m = re.search(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n#]+)", content, re.M)
    return m.group(1).strip() if m else None

def extract_metadata(path: Path, content: str) -> dict:
    return {
        "title": yaml_scalar(content, "title") or path.stem,
        "source_type": yaml_scalar(content, "source_type") or "repository_document",
        "verification_status": yaml_scalar(content, "verification_status") or "needs-verification",
        "effective_status": yaml_scalar(content, "effective_status") or "unknown",
        "article": yaml_scalar(content, "article"),
        "law_number": yaml_scalar(content, "law_number"),
        "year": yaml_scalar(content, "year"),
    }

def split_chunks(path: Path, content: str, max_chars: int = 1800) -> Iterable[Chunk]:
    meta = extract_metadata(path, content)
    sections = re.split(r"(?=^#{1,4}\s+)", content, flags=re.M)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        for i in range(0, len(section), max_chars):
            piece = section[i:i+max_chars].strip()
            if piece:
                yield Chunk(
                    path.as_posix(), meta["title"], piece, meta["source_type"],
                    meta["verification_status"], meta["effective_status"],
                    meta["article"], meta["law_number"], meta["year"]
                )

class LegalRetriever:
    def __init__(self, root: str | Path = "."):
        self.root = Path(root)
        self.chunks: list[Chunk] = []

    def build(self) -> int:
        self.chunks.clear()
        for path in self.root.rglob("*"):
            if not path.is_file() or ".git" in path.parts or ".github" in path.parts:
                continue
            if path.suffix.lower() not in {".md", ".yml", ".yaml", ".json"}:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            self.chunks.extend(split_chunks(path, content))
        return len(self.chunks)

    def search(self, query: str, limit: int = 8) -> list[dict]:
        qtokens = tokens(query)
        if not qtokens:
            return []
        legal_numbers = set(re.findall(r"\b(?:\d{1,4}|\d{1,4}/\d{1,4})\b", normalize_arabic(query)))
        scored = []
        for c in self.chunks:
            haystack = c.text + " " + c.title + " " + c.path
            ctokens = tokens(haystack)
            overlap = len(qtokens & ctokens)
            if not overlap:
                continue
            score = overlap / max(len(qtokens), 1)
            for n in legal_numbers:
                if n in normalize_arabic(haystack):
                    score += 0.35
            if c.verification_status == "verified":
                score += 0.12
            elif c.verification_status == "needs-verification":
                score -= 0.05
            if c.effective_status == "superseded":
                score -= 0.20
            scored.append((score, c))
        scored.sort(key=lambda x: (-x[0], x[1].path))
        return [
            {"score": round(score, 4), **asdict(c), "citation": c.citation()}
            for score, c in scored[:limit]
        ]

def answer_context(results: list[dict]) -> dict:
    return {
        "sources": [
            {
                "citation": r["citation"],
                "path": r["path"],
                "verification_status": r["verification_status"],
                "effective_status": r["effective_status"],
                "score": r["score"],
            } for r in results
        ],
        "context": "\n\n".join(
            f"[{i+1}] {r['citation']}\n{r['text']}"
            for i, r in enumerate(results)
        )
    }

def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Yemeni Legal Assistant retrieval engine")
    p.add_argument("query", nargs="?", help="legal question")
    p.add_argument("--root", default=".")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    retriever = LegalRetriever(args.root)
    count = retriever.build()
    results = retriever.search(args.query or "", args.limit)
    payload = {"indexed_chunks": count, "results": results, **answer_context(results)}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Indexed chunks: {count}")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['citation']} | score={r['score']}")
            print(r["text"][:900])

if __name__ == "__main__":
    main()
