"""
한줄 상담 파이프라인.

흐름:
  1. Guard + 카테고리 분류 (llm.guard)
  2. Engine.calculate_saju()
  3. question-centric RAG + Reranking (llm.reranker)
  4. generate_consultation() — 1탭, 500자
"""

from __future__ import annotations
import asyncio
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from engine.handlers.calculate_saju import handle_calculate_saju
from engine.handlers.get_wol_un import handle_get_wol_un
from engine.handlers.get_yeon_un import handle_get_yeon_un
from llm.guard import guard_and_classify
from llm.reranker import rerank_chunks, build_question_query, CATEGORY_QUERY_HINT, CATEGORY_TAG_MAP
from llm.writer import generate_consultation
from rag.db import search_multi
from rag.search import handle_get_ilju_profile

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="question-pipeline")

# 시기 분석이 유의미한 카테고리
_TIMING_CATEGORIES = {"love", "career", "money"}


def _build_question_rag(
    saju: dict,
    question: str,
    category: str,
) -> dict:
    """
    question-centric RAG 조립 + Reranking.

    Returns:
        {
          "chunks":        [reranked RAG chunk, ...],  # 상위 4개
          "ilju":          {일주 전체 지식} or None,
          "strength":      str | None,
          "yong_sin_summary": str | None,
        }
    """
    yong_sin = saju.get("yong_sin", {})
    ys_elements = [yong_sin.get("primary")] + yong_sin.get("xi_sin", [])
    ys_elements = [e for e in ys_elements if e]
    ji_elements = yong_sin.get("ji_sin", [])

    # core_keywords: life_domains 태그 + context_ranking top IDs
    life_domains = saju.get("life_domains", {})
    core_kw: list[str] = []
    for tags in life_domains.values():
        core_kw.extend(tags[:2])
    core_kw = core_kw[:3]
    ctx_top = saju.get("context_ranking", {}).get("primary_context", [])
    core_kw += [c.get("id", "") for c in ctx_top[:2]]

    query = build_question_query(question, category, core_kw)

    # 검색: 고민 관련 컬렉션
    raw_results = search_multi(query, ["ten_gods", "sin_sal", "structure_patterns", "ilju"], 3)
    all_chunks: list[dict] = []
    for hits in raw_results.values():
        all_chunks.extend(hits)

    # Reranking
    reranked = rerank_chunks(all_chunks, ys_elements, ji_elements, category)

    # 일주 직접 조회 (CORE)
    dp = saju.get("day_pillar", {})
    day_pillar_str = dp.get("stem", "") + dp.get("branch", "")
    ilju = handle_get_ilju_profile(day_pillar_str) if day_pillar_str else None

    # 신강신약 + 용신 요약
    dms = saju.get("day_master_strength", {})
    ys  = saju.get("yong_sin", {})
    xi  = "·".join(ys.get("xi_sin", []))

    # 세운 + 월운: 시기가 의미 있는 카테고리에만 포함
    today    = datetime.now()
    day_stem = dp.get("stem", "")
    if category in _TIMING_CATEGORIES:
        se_un  = handle_get_yeon_un(today.year, 2, day_stem)
        wol_un = handle_get_wol_un(today.year, day_stem)
    else:
        se_un  = []
        wol_un = []

    return {
        "chunks":           reranked,
        "ilju":             ilju,
        "strength":         dms.get("level_8"),
        "yong_sin_summary": f"용신:{ys.get('primary','')} ({ys.get('logic_type','')}), 희신:{xi}",
        "se_un":            se_un,
        "wol_un":           wol_un,
        "current_month":    today.month,
    }


async def run_question_consultation(
    birth_date: str,
    birth_time: str | None,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    birth_longitude: float | None = None,
    birth_utc_offset: int | None = None,
    question: str = "",
    llm_provider: str | None = None,
) -> dict:
    """
    한줄 상담 파이프라인.

    Returns:
        {"headline": str, "content": str}
    """
    loop = asyncio.get_running_loop()

    # 0. Guard + 카테고리 자동 분류 (LLM 1회 호출)
    guard_msg, category, is_instant = await guard_and_classify(question, llm_provider)
    if is_instant:
        logger.info("Instant answer: %s", question[:30])
        if guard_msg and "|||" in guard_msg:
            headline, content = guard_msg.split("|||", 1)
        else:
            headline, content = "잠깐만요", guard_msg or ""
        return {"headline": headline, "content": content, "category": category}

    is_medical = (guard_msg == "MEDICAL")
    if is_medical:
        guard_msg = None  # 차단 아님 — 파이프라인 계속 실행
        logger.info("Medical question detected, will add disclaimer")

    if guard_msg:
        logger.info("Guard blocked question: %s", question[:30])
        return {
            "headline": "사주는 덕(德)을 쌓는 자에게 길(吉)을 줍니다",
            "content": guard_msg,
            "category": category,
        }
    logger.info("Guard passed, category=%s", category)

    # 1. Engine
    calc_fn = functools.partial(
        handle_calculate_saju,
        birth_date=birth_date,
        birth_time=birth_time,
        gender=gender,
        calendar=calendar,
        is_leap_month=is_leap_month,
        birth_longitude=birth_longitude,
        birth_utc_offset=birth_utc_offset,
    )
    saju: dict = await loop.run_in_executor(_executor, calc_fn)
    logger.info("Question 사주 계산 완료: %s%s",
                saju.get("day_pillar", {}).get("stem", ""),
                saju.get("day_pillar", {}).get("branch", ""))

    # 2. RAG + Reranking (MEDICAL은 RAG 청크 제외 — 일주론+대운만)
    rag_fn = functools.partial(_build_question_rag, saju, question, category)
    rag_ctx: dict = await loop.run_in_executor(_executor, rag_fn)
    if is_medical:
        rag_ctx["chunks"] = []  # 불필요한 청크로 내용 팽창 방지
    logger.info("Question RAG 완료: chunks=%d", len(rag_ctx.get("chunks", [])))

    # 3. Writer
    effective_question = (
        f"{question}\n\n[주의사항]\n"
        f"1. 수술·치료법 선택 등 의료적 결정에 대한 권고는 절대 하지 마세요.\n"
        f"2. 신살(귀문관살 등)을 특정 질병의 원인으로 직접 연결하지 마세요.\n"
        f"3. 계절·시기 언급은 월운 데이터가 제공된 경우에만 하세요. 지어내지 마세요.\n"
        f"4. 사주의 에너지 흐름(용신·대운 기준)만 이야기하세요.\n"
        f"5. 마지막 문장은 반드시 '구체적인 치료 결정은 의료진과 상담하세요'로 끝내세요."
        if is_medical else question
    )
    output = await generate_consultation(saju, rag_ctx, effective_question, category, llm_provider)
    return {"headline": output.headline, "content": output.content, "category": category}
