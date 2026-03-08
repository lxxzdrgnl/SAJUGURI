"""
RAG 검색 tool 핸들러.
"""

from __future__ import annotations
import json
from lib.db import search, search_multi, COLLECTIONS


def handle_search_knowledge(
    query: str,
    categories: list[str] | None = None,
    n_results: int = 3,
    where: dict | None = None,
) -> dict:
    """
    지식 베이스 시맨틱 검색.

    Args:
        query:      자연어 검색 쿼리 (사용자 고민, 사주 맥락 등)
        categories: 검색할 카테고리 목록. None이면 전체 검색
                    ["ten_gods", "sin_sal", "gyeok_guk", "structure_patterns", "wuxing", "ilju"]
        n_results:  카테고리당 반환할 결과 수 (기본 3)
        where:      메타데이터 필터 예: {"category": "ten_gods"} or {"element": "수"}

    Returns:
        {category: [{id, document, metadata, distance}]}
    """
    if categories and len(categories) == 1 and where is None:
        results = search(categories[0], query, n_results, where)
        return {categories[0]: results}
    return search_multi(query, categories, n_results)


def handle_get_ilju_profile(ilju: str) -> dict | None:
    """
    일주(예: '임자', '경오') 직접 조회.

    Args:
        ilju: 한글 일주 이름 (예: '임자', '갑자')

    Returns:
        해당 일주 전체 지식 문서 or None
    """
    import json
    from pathlib import Path

    filepath = Path(__file__).parent.parent / "knowledge" / "ilju.json"
    if not filepath.exists():
        return None

    with open(filepath, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    for entry in entries:
        if entry.get("ilju") == ilju:
            return entry
    return None


def handle_get_ten_god_profile(ten_god_name: str) -> dict | None:
    """
    십성 이름으로 전체 지식 직접 조회.

    Args:
        ten_god_name: 한글 십성 이름 (예: '비견', '식신', '편재')

    Returns:
        해당 십성 전체 지식 문서 or None
    """
    from pathlib import Path

    filepath = Path(__file__).parent.parent / "knowledge" / "ten_gods.json"
    if not filepath.exists():
        return None

    with open(filepath, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    for entry in entries:
        if entry.get("name") == ten_god_name:
            return entry
    return None


def handle_get_structure_pattern(pattern_type: str) -> dict | None:
    """
    구조 패턴 타입으로 전체 지식 직접 조회.

    Args:
        pattern_type: 예: 'sig_sang_saeng_jae', 'gwan_in_sang_saeng'

    Returns:
        해당 패턴 전체 지식 문서 or None
    """
    from pathlib import Path

    filepath = Path(__file__).parent.parent / "knowledge" / "structure_patterns.json"
    if not filepath.exists():
        return None

    with open(filepath, encoding="utf-8") as f:
        entries: list[dict] = json.load(f)

    for entry in entries:
        if entry.get("type") == pattern_type:
            return entry
    return None
