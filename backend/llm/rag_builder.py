"""
RAG 컨텍스트 빌더.

Engine 계산 결과(saju dict)를 받아 Writer LLM에 전달할
RAG 청크를 조립한다. 모든 처리는 결정론적(deterministic)이며
LLM 호출 없이 ChromaDB + knowledge JSON 직접 조회.

v2: Writer 토큰 절약을 위한 컨텍스트 압축 추가.
"""

from __future__ import annotations
from rag.search import handle_search_by_context


# Writer에 불필요한 필드 — 제거 대상
_STRIP_FIELDS_ILJU = {
    "compatibility", "activation_rule", "interpretation_scope",
    "energy_profile", "core_keywords", "id",
}
_STRIP_FIELDS_SIN_SAL = {
    "activation_rule", "interpretation_scope", "id",
}
_STRIP_FIELDS_PATTERN = {
    "interpretation_scope", "id",
}
_STRIP_FIELDS_DOMAIN = {
    "activation_rule", "interpretation_scope", "id",
    "compatibility", "energy_profile", "core_keywords",
}


def _strip_fields(entry: dict, fields: set[str]) -> dict:
    """지정된 필드를 제거한 사본 반환."""
    return {k: v for k, v in entry.items() if k not in fields}


def _compress_ilju(ilju: dict | None) -> dict | None:
    """일주 지식에서 Writer에 불필요한 필드 제거."""
    if not ilju:
        return None
    return _strip_fields(ilju, _STRIP_FIELDS_ILJU)


def _compress_sin_sal(sin_sal_list: list[dict]) -> list[dict]:
    """신살 데이터 압축: data 내부 불필요 필드 제거."""
    compressed = []
    for ss in sin_sal_list:
        entry = dict(ss)
        if "data" in entry:
            entry["data"] = _strip_fields(entry["data"], _STRIP_FIELDS_SIN_SAL)
        compressed.append(entry)
    return compressed


def _compress_context(context_list: list[dict]) -> list[dict]:
    """context(패턴/신살) 데이터 압축."""
    compressed = []
    for ctx in context_list:
        entry = dict(ctx)
        if "data" in entry:
            strip = _STRIP_FIELDS_SIN_SAL if ctx.get("type") == "sin_sal" else _STRIP_FIELDS_PATTERN
            entry["data"] = _strip_fields(entry["data"], strip)
        compressed.append(entry)
    return compressed


def _compress_domain(domain_hits: list[dict]) -> list[dict]:
    """도메인 매칭 결과 압축: data 내부 불필요 필드 제거."""
    compressed = []
    for hit in domain_hits:
        entry = dict(hit)
        if "data" in entry:
            entry["data"] = _strip_fields(entry["data"], _STRIP_FIELDS_DOMAIN)
        compressed.append(entry)
    return compressed


def build_rag_context(saju: dict, concern: str | None = None) -> dict:
    """
    Engine 출력 전체 → Writer용 RAG 컨텍스트 조립 + 압축.

    Args:
        saju    : handle_calculate_saju() 반환 dict
        concern : 사용자 고민 원문 (없으면 None)

    Returns:
        압축된 RAG 컨텍스트 dict
    """
    day_pillar_info = saju.get("day_pillar", {})
    day_pillar_str = (
        day_pillar_info.get("stem", "") + day_pillar_info.get("branch", "")
    )

    raw = handle_search_by_context(
        context_ranking=saju.get("context_ranking", {}),
        life_domains=saju.get("life_domains", {}),
        day_pillar=day_pillar_str or None,
        concern=concern,
        branch_relations=saju.get("branch_relations"),
        dynamics=saju.get("dynamics"),
        day_master_strength=saju.get("day_master_strength"),
        yong_sin=saju.get("yong_sin"),
        sin_sals=saju.get("sin_sals"),
    )

    # 컨텍스트 압축 — Writer 토큰 절약
    return {
        # 도메인별 태그 매칭 결과 (압축)
        "career":       _compress_domain(raw.get("career", [])),
        "relationship": _compress_domain(raw.get("relationship", [])),
        "wealth":       _compress_domain(raw.get("wealth", [])),
        "personality":  _compress_domain(raw.get("personality", [])),
        # 구조 컨텍스트 (압축)
        "context":      _compress_context(raw.get("context", [])),
        # 일주 (압축)
        "ilju":         _compress_ilju(raw.get("ilju")),
        # concern 시맨틱 검색 결과 (원본 유지 — 이미 경량)
        "concern":       raw.get("concern", []),
        "concern_hints": raw.get("concern_hints", []),
        # dynamics 직접 조회 결과
        "dynamics":      raw.get("dynamics", []),
        # 신살 (압축)
        "sin_sal_all":   _compress_sin_sal(raw.get("sin_sal_all", [])),
        # 메타데이터 (원본 유지)
        "strength":         raw.get("strength"),
        "yong_sin_summary": raw.get("yong_sin_summary"),
    }
