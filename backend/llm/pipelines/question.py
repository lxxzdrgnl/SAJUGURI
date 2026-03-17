"""
한줄 상담 파이프라인.

흐름:
  1. Engine.calculate_saju()
  2. question-centric RAG (question + category + core_keywords[:3])
  3. 용신/기신 기반 Reranking (_rerank_chunks)
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
from llm.writer import generate_consultation
from llm.providers import get_llm
from rag.db import search_multi
from rag.search import _find_by_field

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="question-pipeline")

# ── 오행 키워드 매핑 ─────────────────────────────────────────────────────────
ELEMENT_KEYWORDS: dict[str, list[str]] = {
    "목": ["목", "木", "갑", "을", "인", "묘"],
    "화": ["화", "火", "병", "정", "사", "오"],
    "토": ["토", "土", "무", "기", "진", "술", "축", "미"],
    "금": ["금", "金", "경", "신", "유"],
    "수": ["수", "水", "임", "계", "자", "해"],
}

# ── 카테고리 → RAG 힌트 키워드 ───────────────────────────────────────────────
CATEGORY_QUERY_HINT: dict[str, str] = {
    "career":  "직업 이직 승진 사업 직장",
    "love":    "연애 결혼 배우자 인연 이성",
    "money":   "재물 투자 수입 재산 돈",
    "health":  "건강 체력 기운 스트레스 몸",
    "general": "",
}

CATEGORY_TAG_MAP: dict[str, list[str]] = {
    "career":  ["career", "promotion", "business", "job", "leadership"],
    "love":    ["relationship", "marriage", "romance", "partner", "attraction"],
    "money":   ["wealth", "investment", "income", "finance"],
    "health":  ["health", "energy", "vitality", "stress"],
    "general": [],
}


def _build_question_query(question: str, category: str, core_keywords: list[str]) -> str:
    """
    RAG 검색용 쿼리 문자열 조립.
    question + category 힌트 + core_keywords 최대 3개
    """
    parts = [question]
    if hint := CATEGORY_QUERY_HINT.get(category, ""):
        parts.append(hint)
    parts.extend(core_keywords[:3])
    return " ".join(filter(None, parts))


def _rerank_chunks(
    chunks: list[dict],
    yong_sin: list[str],
    ji_sin: list[str],
    category: str,
) -> list[dict]:
    """
    용신/기신 기반 Reranking.

    - 용신 오행 관련 키워드 포함 시: score -= 0.2 (boost)
    - 기신 오행 관련 키워드 포함 시: score += 0.3 (penalize)
    - category 매칭 interpretation_tag 포함 시: score -= 0.1 (bonus)
    - 결과: 상위 4개만 반환
    """
    if not chunks:
        return []

    scored: list[tuple[float, dict]] = []
    cat_tags = CATEGORY_TAG_MAP.get(category, [])

    for chunk in chunks:
        score = chunk.get("distance") or 0.5
        doc   = chunk.get("document", "").lower()
        meta  = chunk.get("metadata", {})
        interp_tags = meta.get("interpretation_tags", "").lower()
        combined = doc + " " + interp_tags

        # 용신 boost (먼저 적용)
        yong_boosted = False
        for el in yong_sin:
            if any(kw in combined for kw in ELEMENT_KEYWORDS.get(el, [])):
                score -= 0.2
                yong_boosted = True
                break

        # 기신 penalize (용신 boost가 없을 때만 적용 — 양쪽 포함 청크는 boost 우선)
        if not yong_boosted:
            for el in ji_sin:
                if any(kw in combined for kw in ELEMENT_KEYWORDS.get(el, [])):
                    score += 0.3
                    break

        # 카테고리 bonus
        if cat_tags and any(t in interp_tags for t in cat_tags):
            score -= 0.1

        chunk = dict(chunk)
        chunk["_rerank_score"] = score
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0])
    return [c for _, c in scored[:4]]


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

    # core_keywords: life_domains 태그 (한국어) + context_ranking top IDs
    # ※ behavior_profile은 영문 벡터라 한국어 ChromaDB 검색에 부적합 — life_domains 사용
    life_domains = saju.get("life_domains", {})
    core_kw: list[str] = []
    for tags in life_domains.values():
        core_kw.extend(tags[:2])
    core_kw = core_kw[:3]
    ctx_top = saju.get("context_ranking", {}).get("primary_context", [])
    core_kw += [c.get("id", "") for c in ctx_top[:2]]

    query = _build_question_query(question, category, core_kw)

    # 검색: 고민 관련 컬렉션
    raw_results = search_multi(query, ["ten_gods", "sin_sal", "structure_patterns", "ilju"], 3)
    all_chunks: list[dict] = []
    for hits in raw_results.values():
        all_chunks.extend(hits)

    # Reranking
    reranked = _rerank_chunks(all_chunks, ys_elements, ji_elements, category)

    # 일주 직접 조회 (CORE)
    dp = saju.get("day_pillar", {})
    day_pillar_str = dp.get("stem", "") + dp.get("branch", "")
    ilju = _find_by_field("ilju", "ilju", day_pillar_str) if day_pillar_str else None

    # 신강신약 + 용신 요약
    dms = saju.get("day_master_strength", {})
    ys  = saju.get("yong_sin", {})
    xi  = "·".join(ys.get("xi_sin", []))

    # 세운 + 월운: 시기가 의미 있는 카테고리에만 포함
    today    = datetime.now()
    day_stem = dp.get("stem", "")
    TIMING_CATEGORIES = {"love", "career", "money"}
    if category in TIMING_CATEGORIES:
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


_GUARD_PROMPT = """사용자의 고민을 보고 아래 네 가지 중 하나로 분류하세요.

[BLOCK] 아래에 해당하면 차단:
- 타인의 신체 접촉·성적 행위 요청
- 범죄·폭력·불법 행위 조언 요청
- 특정인 비방·스토킹·위협

[MEDICAL] 실제 의료 결정이 필요한 상황. 아래 조건을 **모두** 충족해야 MEDICAL:
- 실제로 발생 가능한 의료 상황이어야 함
- 수술·약 복용·치료법·병원 방문 여부를 진지하게 고민하는 경우
→ "건강 운세" 질문은 OK|health.
→ 전제 자체가 비현실적이거나 농담성 질문은 MEDICAL 아님.
  예: "엉덩이가 커서 절단할까?" → 절단은 비현실적 전제 → INSTANT로 유머 처리
  예: "IBS 때문에 수술할까?" → IBS는 수술 적응증 아님 → INSTANT로 전제 교정

[INSTANT] 아래 둘 중 하나에만 해당하면 INSTANT:
- 즉각 행동이 답인 생리적 상황 (배고픔, 졸림, 화장실 등)
- 전제 자체가 물리적으로 불가능한 황당한 질문 (예: "팔을 자를까", "화성에 이민 갈까")
→ 짧고 유쾌하게, 사주 특유의 말투로 한 문장 답변. 전제가 틀렸으면 먼저 짚어줄 것.

[OK] 그 외 **모든** 질문. 게임·오락·재미·음식·쇼핑·일상 고민도 모두 OK. 카테고리 분류:
career(직업·이직·사업·시험) / love(연애·결혼·인간관계) / money(재물·투자) / health(건강·체력) / general(기타)

반드시 아래 형식으로만 응답 (다른 텍스트 금지):
OK|<카테고리>
또는
BLOCK: <사주 관점의 한 줄 경고문>
또는
INSTANT: <한 문장 직접 답변>
또는
MEDICAL"""


async def _guard_and_classify(question: str, provider: str | None = None) -> tuple[str | None, str, bool]:
    """
    Guard + 카테고리 자동 분류를 LLM 호출 1회로 처리.

    Returns:
        (block_msg, category, is_instant)
        block_msg:  차단 시 경고 문구, 통과 시 None
        category:   'career' | 'love' | 'money' | 'health' | 'general'
        is_instant: True면 즉시 답변 반환 (사주 분석 생략)
    """
    from langchain_core.messages import SystemMessage, HumanMessage
    llm = get_llm(provider)
    resp = await llm.ainvoke([
        SystemMessage(content=_GUARD_PROMPT),
        HumanMessage(content=f"고민: {question}"),
    ])
    raw = (resp.content if hasattr(resp, "content") else str(resp)).strip()

    if raw.startswith("BLOCK:"):
        return raw[len("BLOCK:"):].strip(), "general", False

    if raw.strip() == "MEDICAL":
        return "MEDICAL", "health", False

    if raw.startswith("INSTANT:"):
        msg = raw[len("INSTANT:"):].strip()
        return msg, "general", True

    # OK|career 형식 파싱
    category = "general"
    if "|" in raw:
        category = raw.split("|", 1)[1].strip().lower()
        if category not in ("career", "love", "money", "health", "general"):
            category = "general"

    # LLM이 놓친 경우 키워드 폴백 — 미용·성형 시술은 제외, 진짜 의료 결정만
    _MEDICAL_KW = ("약 복용", "치료법", "처방", "입원", "항생제", "진통제", "항암", "방사선치료")
    if any(kw in question for kw in _MEDICAL_KW):
        return "MEDICAL", "health", False

    return None, category, False


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
    guard_msg, category, is_instant = await _guard_and_classify(question, llm_provider)
    if is_instant:
        logger.info("Instant answer: %s", question[:30])
        return {"headline": "지금 바로 해결하세요", "content": guard_msg, "category": category}

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
