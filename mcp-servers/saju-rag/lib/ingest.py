"""
knowledge/ JSON → ChromaDB 인덱싱.
각 카테고리별로 document 텍스트를 구성하여 임베딩 후 저장.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from lib.db import get_collection

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def _build_document(entry: dict, category: str) -> str:
    """
    벡터 검색에 쓸 document 텍스트 생성.
    semantic_context가 있으면 우선 사용, 없으면 주요 필드 조합.
    """
    parts: list[str] = []

    if ctx := entry.get("semantic_context"):
        parts.append(ctx)

    name = entry.get("name", "")
    hanja = entry.get("hanja", "")
    if name:
        parts.append(f"{name}({hanja})")

    for field in ["personality", "career", "relationship", "core", "strength",
                  "desc", "positive", "modern", "modern_advice"]:
        if val := entry.get(field):
            parts.append(val)

    if cp := entry.get("consulting_points"):
        if trigger := cp.get("empathy_trigger"):
            parts.append(trigger)
        if speech := cp.get("solution_speech"):
            parts.append(speech)

    return " ".join(parts)


def _build_metadata(entry: dict, category: str) -> dict:
    """ChromaDB 메타데이터 — where 필터용."""
    meta: dict = {"category": category}
    for key in ["id", "name", "hanja", "type", "element", "ilju", "stem", "branch",
                "yin_yang", "season", "tab_headline"]:
        if val := entry.get(key):
            meta[key] = val
    # consulting_points.tab_headline 추출
    if cp := entry.get("consulting_points"):
        if hl := cp.get("tab_headline"):
            meta["tab_headline"] = hl
    # tags → 콤마 구분 문자열
    if tags := entry.get("tags"):
        meta["tags"] = ",".join(tags)
    return meta


def ingest_category(category: str) -> int:
    """
    knowledge/{category}.json → ChromaDB collection.
    기존 데이터는 upsert로 덮어씀.

    Returns:
        삽입된 문서 수
    """
    filepath = KNOWLEDGE_DIR / f"{category}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Knowledge file not found: {filepath}")

    with open(filepath, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    col = get_collection(category)

    ids = [e["id"] for e in entries]
    documents = [_build_document(e, category) for e in entries]
    metadatas = [_build_metadata(e, category) for e in entries]

    col.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(entries)


def ingest_all() -> dict[str, int]:
    """
    모든 카테고리 인덱싱.

    Returns:
        {category: count}
    """
    categories = [p.stem for p in KNOWLEDGE_DIR.glob("*.json")]
    return {cat: ingest_category(cat) for cat in sorted(categories)}


if __name__ == "__main__":
    results = ingest_all()
    for cat, count in results.items():
        print(f"  {cat}: {count}개 문서 인덱싱 완료")
