"""
RAG 컨텍스트 빌더.

Engine 계산 결과(saju dict)를 받아 Writer LLM에 전달할
RAG 청크를 조립한다. 모든 처리는 결정론적(deterministic)이며
LLM 호출 없이 ChromaDB + knowledge JSON 직접 조회.
"""

from __future__ import annotations
from rag.search import handle_search_by_context


def build_rag_context(saju: dict, concern: str | None = None) -> dict:
    """
    Engine 출력 전체 → Writer용 RAG 컨텍스트 조립.

    Args:
        saju    : handle_calculate_saju() 반환 dict
        concern : 사용자 고민 원문 (없으면 None)

    Returns:
        handle_search_by_context() 형식의 dict:
        {
          "career":        [RAG chunk, ...],
          "relationship":  [RAG chunk, ...],
          "wealth":        [RAG chunk, ...],
          "personality":   [RAG chunk, ...],
          "context":       [{"id", "type", "data"}, ...],
          "ilju":          {일주 전체 지식} or None,
          "concern":       [RAG chunk, ...],
          "dynamics":      [RAG chunk, ...],
          "strength":      str | None,
          "yong_sin_summary": str | None,
        }
    """
    day_pillar_info = saju.get("day_pillar", {})
    day_pillar_str = (
        day_pillar_info.get("stem", "") + day_pillar_info.get("branch", "")
    )

    return handle_search_by_context(
        context_ranking=saju.get("context_ranking", {}),
        life_domains=saju.get("life_domains", {}),
        day_pillar=day_pillar_str or None,
        concern=concern,
        branch_relations=saju.get("branch_relations"),
        dynamics=saju.get("dynamics"),
        day_master_strength=saju.get("day_master_strength"),
        yong_sin=saju.get("yong_sin"),
    )
