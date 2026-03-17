# 한줄 상담 (Question Consultation) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `POST /api/question` 엔드포인트 + 프론트 페이지를 구현하여, 생년월일 + 카테고리 + 고민을 입력하면 용신 기반 reranking을 거친 AI 단답형 상담(headline + content)을 반환한다.

**Architecture:** Engine.calculate_saju() → question-centric RAG (concern 시맨틱 + saju core_keywords) → 용신/기신 기반 Reranking → Writer LLM (Chain-of-Thought 1탭). 프론트는 daily/index.vue 동일 패턴(select → input/profile → question → result).

**Tech Stack:** FastAPI, Pydantic v2, LangChain, ChromaDB, Vue 3 / Nuxt 3, TypeScript

---

## File Map

| 작업 | 파일 | 역할 |
|---|---|---|
| Create | `backend/schemas/question.py` | QuestionRequest (category + question), ConsultationOutput |
| Create | `backend/llm/pipelines/question.py` | Engine → RAG → Rerank → Writer 파이프라인 |
| Modify | `backend/llm/prompts.py` | `QUESTION_SYSTEM_PROMPT` + `format_question_message()` 추가 |
| Modify | `backend/llm/writer.py` | `generate_consultation()` 추가 |
| Create | `backend/routers/question.py` | `POST /api/question` 라우터 |
| Modify | `backend/main.py` | `question.router` 등록 (주석 해제) |
| Modify | `backend/tests/test_question_pipeline.py` | 파이프라인 단위 테스트 |
| Modify | `frontend/types/saju.ts` | `QuestionRequest`, `ConsultationResponse` 타입 추가 |
| Modify | `frontend/composables/useSajuApi.ts` | `askQuestion()` 함수 추가 |
| Create | `frontend/pages/question/index.vue` | 한줄 상담 페이지 |

---

## Chunk 1: 백엔드 — Schema + Pipeline + Router

### Task 1: Schema (`schemas/question.py`)

**Files:**
- Create: `backend/schemas/question.py`

- [ ] **Step 1: 파일 생성**

```python
"""한줄 상담 요청/응답 Pydantic 스키마."""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


CATEGORIES = Literal['career', 'love', 'money', 'health', 'general']


class QuestionRequest(BaseModel):
    """한줄 상담 요청."""

    birth_date: str = Field(description="생년월일 (YYYY-MM-DD)", examples=["1990-03-15"])
    birth_time: str | None = Field(default=None, description="출생 시각 (HH:MM). 모를 경우 null", examples=["14:30"])
    gender: str = Field(description="성별", examples=["male"], pattern="^(male|female)$")
    calendar: str = Field(default="solar", pattern="^(solar|lunar)$")
    is_leap_month: bool = Field(default=False)
    birth_longitude: float | None = Field(default=None)
    birth_utc_offset: int | None = Field(default=None)

    question: str = Field(
        description="고민 원문 (10~200자)",
        min_length=10,
        max_length=200,
        examples=["올해 이직 운이 있을까요?"],
    )
    category: CATEGORIES = Field(
        default='general',
        description="고민 카테고리. 모호한 질문의 RAG 정확도 향상에 사용",
        examples=["career"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "birth_date": "1990-03-15",
                "birth_time": "14:30",
                "gender": "male",
                "calendar": "solar",
                "is_leap_month": False,
                "question": "올해 이직 운이 있을까요?",
                "category": "career",
            }
        }
    }


class ConsultationOutput(BaseModel):
    """한줄 상담 Writer 출력."""
    headline: str = Field(
        description="결론형 한 문장 (30자 내외)",
        examples=["변화의 파도가 이미 당신 발아래까지 왔습니다"],
    )
    content: str = Field(
        description="상세 내용 (300~500자)",
        examples=["정관격에 식상운이 들어온 지금..."],
    )


class QuestionResponse(BaseModel):
    """한줄 상담 API 응답."""
    headline: str
    content: str
    category: str
```

- [ ] **Step 2: 문법 검증**

```bash
cd backend && python3 -c "from schemas.question import QuestionRequest, ConsultationOutput, QuestionResponse; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/schemas/question.py
git commit -m "feat: add QuestionRequest and ConsultationOutput schemas"
```

---

### Task 2: RAG + Reranking (`llm/pipelines/question.py`)

**Files:**
- Create: `backend/llm/pipelines/question.py`

핵심 로직: `_rerank_chunks()` — 용신 오행 포함 시 score -0.2 (boost), 기신 포함 시 +0.3 (penalize).

- [ ] **Step 1: 테스트 먼저 작성 (`tests/test_question_pipeline.py`)**

```python
"""한줄 상담 파이프라인 단위 테스트."""

import pytest
from llm.pipelines.question import _rerank_chunks, _build_question_query, ELEMENT_KEYWORDS


BIRTH = dict(
    birth_date="1990-03-15",
    birth_time="14:30",
    gender="male",
    calendar="solar",
)


class TestReranking:
    """_rerank_chunks — 용신 boost / 기신 penalize."""

    def _make_chunk(self, doc: str, tags: str = "") -> dict:
        return {
            "id": "test",
            "document": doc,
            "metadata": {"interpretation_tags": tags},
            "distance": 0.5,
        }

    def test_yong_sin_boost_lowers_score(self):
        """용신(수) 포함 청크는 score가 내려간다 (더 우선)."""
        chunk = self._make_chunk("수기(水氣)가 강해지는 시기에 용기를 내세요")
        result = _rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화", "토"], category="general")
        # boost: 0.5 - 0.2 = 0.3
        assert result[0]["_rerank_score"] < 0.5

    def test_ji_sin_penalty_raises_score(self):
        """기신(화) 포함 청크는 score가 올라간다 (후순위)."""
        chunk = self._make_chunk("화기(火氣)로 승부를 걸어보세요")
        result = _rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화", "토"], category="general")
        # penalty: 0.5 + 0.3 = 0.8
        assert result[0]["_rerank_score"] > 0.5

    def test_category_bonus_lowers_score(self):
        """category 매칭 interpretation_tag 포함 시 score 추가 감소."""
        chunk = self._make_chunk("직업 변화", tags="career_change,promotion")
        result = _rerank_chunks([chunk], yong_sin=[], ji_sin=[], category="career")
        assert result[0]["_rerank_score"] < 0.5

    def test_ordering_yong_before_ji(self):
        """용신 청크가 기신 청크보다 앞에 온다."""
        good = self._make_chunk("수기 관련 조언")
        bad  = self._make_chunk("화기 관련 일반론")
        result = _rerank_chunks([bad, good], yong_sin=["수"], ji_sin=["화"], category="general")
        assert "수기" in result[0]["document"]

    def test_chunk_with_both_yong_and_ji_gets_boost_not_penalty(self):
        """용신과 기신 키워드 모두 포함 시 boost만 적용 (penalty 무시)."""
        chunk = self._make_chunk("수기가 강하면 화기를 억제한다")
        result = _rerank_chunks([chunk], yong_sin=["수"], ji_sin=["화"], category="general")
        # 용신 boost만: 0.5 - 0.2 = 0.3 (penalty +0.3 미적용)
        assert result[0]["_rerank_score"] < 0.5

    def test_returns_max_four_chunks(self):
        """최대 4개까지만 반환."""
        chunks = [self._make_chunk(f"내용 {i}") for i in range(10)]
        result = _rerank_chunks(chunks, yong_sin=[], ji_sin=[], category="general")
        assert len(result) <= 4

    def test_empty_input_returns_empty(self):
        result = _rerank_chunks([], yong_sin=["수"], ji_sin=["화"], category="general")
        assert result == []


class TestQueryBuilder:
    """_build_question_query — question + category + core_keywords 조합."""

    def test_includes_question(self):
        q = _build_question_query("이직해도 될까요?", "career", ["정관", "식신"])
        assert "이직" in q

    def test_includes_category_keyword(self):
        q = _build_question_query("어떻게 될까요?", "career", [])
        assert "직업" in q or "career" in q

    def test_includes_core_keywords(self):
        q = _build_question_query("질문", "general", ["정관", "역마살"])
        assert "정관" in q

    def test_core_keywords_capped_at_three(self):
        keywords = ["a", "b", "c", "d", "e"]
        q = _build_question_query("질문", "general", keywords)
        # 쿼리에 4번째 이후 키워드가 없어야 함
        assert "d" not in q
        assert "e" not in q
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
cd backend && python3 -m pytest tests/test_question_pipeline.py -v 2>&1 | head -20
```
Expected: `ImportError` 또는 `ModuleNotFoundError` (파일 없으니 당연히 실패)

- [ ] **Step 3: 파이프라인 구현**

```python
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

from engine.handlers.calculate_saju import handle_calculate_saju
from llm.writer import generate_consultation
from rag.db import search_multi
from rag.search import _find_by_field  # 모듈 top-level에 위치해야 함

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

    # 일주 직접 조회 (CORE) — 모듈 상단에서 import된 _find_by_field 사용
    dp = saju.get("day_pillar", {})
    day_pillar_str = dp.get("stem", "") + dp.get("branch", "")
    ilju = _find_by_field("ilju", "ilju", day_pillar_str) if day_pillar_str else None

    # 신강신약 + 용신 요약
    dms = saju.get("day_master_strength", {})
    ys  = saju.get("yong_sin", {})
    xi  = "·".join(ys.get("xi_sin", []))

    return {
        "chunks":           reranked,
        "ilju":             ilju,
        "strength":         dms.get("level_8"),
        "yong_sin_summary": f"용신:{ys.get('primary','')} ({ys.get('logic_type','')}), 희신:{xi}",
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
    category: str = "general",
    llm_provider: str | None = None,
) -> dict:
    """
    한줄 상담 파이프라인.

    Returns:
        {"headline": str, "content": str}
    """
    loop = asyncio.get_event_loop()

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

    # 2. RAG + Reranking
    rag_fn = functools.partial(_build_question_rag, saju, question, category)
    rag_ctx: dict = await loop.run_in_executor(_executor, rag_fn)
    logger.info("Question RAG 완료: chunks=%d", len(rag_ctx.get("chunks", [])))

    # 3. Writer
    output = await generate_consultation(saju, rag_ctx, question, category, llm_provider)
    return {"headline": output.headline, "content": output.content}
```

- [ ] **Step 4: 테스트 실행 (Reranking + QueryBuilder만)**

```bash
cd backend && python3 -m pytest tests/test_question_pipeline.py::TestReranking tests/test_question_pipeline.py::TestQueryBuilder -v
```
Expected: 모두 PASS (chromadb 불필요한 테스트만 실행)

- [ ] **Step 5: Commit**

```bash
git add backend/llm/pipelines/question.py backend/tests/test_question_pipeline.py
git commit -m "feat: add question pipeline with yong-sin/ji-sin reranking"
```

---

### Task 3: Prompt + Writer (`llm/prompts.py`, `llm/writer.py`)

**Files:**
- Modify: `backend/llm/prompts.py` — `QUESTION_SYSTEM_PROMPT` + `format_question_message()` 추가
- Modify: `backend/llm/writer.py` — `generate_consultation()` 추가

- [ ] **Step 1: `prompts.py`에 추가**

`format_user_message` 함수 끝 다음에 추가:

```python
# ─── 한줄 상담 전용 ────────────────────────────────────────────────────────────

QUESTION_SYSTEM_PROMPT = """당신은 명리학(사주팔자)에 정통한 AI 상담사입니다.
사주 데이터를 바탕으로 사용자의 고민에 직접 답합니다.

## 추론 규칙 (Chain of Thought)

답변 전, 내부적으로 아래 순서로 분석하세요 (출력에 포함하지 말 것):
1. "이 사람의 격국은 __이고, 용신은 __이다"
2. "현재 대운/세운의 기운은 __이다"
3. "고민(__)은 __ 관점에서 __한 상황이다"
4. 위 분석을 바탕으로 결론형 헤드라인 → 상세 내용 순으로 작성

## 출력 규칙

- headline: 결론형 한 문장 (30자 내외). 카테고리명 금지. 이 사람의 사주에만 해당하는 문장.
  - 나쁜 예: "직업 운 분석" → 좋은 예: "정관격의 책임감이 지금 당신을 더 큰 무대로 부르고 있습니다"
- content: 300~500자. 용신·기신 기반 구체적 조언. 일반론 금지.
- RAG 지식은 직접 인용하지 말고 이 사람의 사주에 적용해서 해석하세요.

## 출력 형식
아래 JSON 형식으로만 응답하세요:
"""

CATEGORY_LABEL: dict[str, str] = {
    "career": "직업·이직",
    "love":   "연애·결혼",
    "money":  "재물·투자",
    "health": "건강",
    "general": "일반",
}


def format_question_message(
    saju: dict,
    rag_ctx: dict,
    question: str,
    category: str,
    format_instructions: str,
) -> str:
    """
    한줄 상담용 LLM 입력 문자열.
    사주 핵심 + CORE RAG + 고민으로 압축 (리포트보다 훨씬 짧게).
    """
    parts: list[str] = []

    # ── 1. 사주 핵심 (압축) ──
    dp  = saju.get("day_pillar", {})
    dms = saju.get("day_master_strength", {})
    ys  = saju.get("yong_sin", {})
    gy  = saju.get("gyeok_guk", {})
    cur = saju.get("current_dae_un", {})

    xi = "·".join(ys.get("xi_sin", []))
    ji = "·".join(ys.get("ji_sin", []))

    parts.append("=== 사주 핵심 ===")
    parts.append(
        f"일주: {dp.get('stem','')}{dp.get('branch','')} ({dp.get('stem_element','')}/{dp.get('branch_element','')})"
    )
    parts.append(f"격국: {gy.get('name','')}")
    parts.append(f"일간 강약: {dms.get('level_8','')} (점수 {dms.get('score','')})")
    parts.append(f"용신: {ys.get('primary','')} ({ys.get('yong_sin_label','')}) / 희신:{xi} / 기신:{ji}")
    if cur:
        parts.append(
            f"현재 대운: {cur.get('start_age','')}~{cur.get('end_age','')}세 "
            f"{cur.get('stem','')}{cur.get('branch','')} ({cur.get('stem_element','')}/{cur.get('branch_element','')})"
        )

    # 주요 신살 (high만)
    sin_sals = saju.get("sin_sals", [])
    high_sals = [s.get("name", "") for s in sin_sals if s.get("priority") == "high"]
    if high_sals:
        parts.append(f"주요 신살: {', '.join(high_sals)}")

    # ── 2. 고민 ──
    cat_label = CATEGORY_LABEL.get(category, "")
    parts.append(f"\n=== 고민 [{cat_label}] ===\n{question}")

    # ── 3. RAG 지식 (CORE만, 압축) ──
    parts.append("\n=== 명리 지식 참고 ===")

    # 신강신약·용신
    if rag_ctx.get("strength"):
        parts.append(f"신강신약: {rag_ctx['strength']}")
    if rag_ctx.get("yong_sin_summary"):
        parts.append(f"용신 요약: {rag_ctx['yong_sin_summary']}")

    # 일주론 핵심
    ilju = rag_ctx.get("ilju")
    if ilju:
        ec = ilju.get("embedding_context", "")
        cp = ilju.get("consulting_points", {})
        hl = cp.get("tab_headline", "")
        if ec:
            parts.append(f"[일주론] {ec[:200]}")
        if hl:
            parts.append(f"[일주 핵심 메시지] {hl}")

    # Reranked chunks
    for chunk in rag_ctx.get("chunks", []):
        doc = chunk.get("document", "")
        if doc:
            parts.append(f"• {doc[:200]}")

    # ── 4. 출력 형식 ──
    parts.append(f"\n=== 출력 형식 ===\n{format_instructions}")

    return "\n".join(parts)
```

- [ ] **Step 2: `writer.py`에 `generate_consultation()` 추가**

**⚠️ import 위치 주의**: 아래 두 줄은 `writer.py` 파일 **상단 import 블록**에 추가. 함수 안이나 중간에 넣으면 안 됨.

```python
# writer.py 상단 import 블록에 추가 (from schemas.report import ... 줄 옆)
from schemas.question import ConsultationOutput
from llm.prompts import QUESTION_SYSTEM_PROMPT, format_question_message
```

그 다음 기존 `generate_report` 함수 아래에 새 함수 추가:

```python


async def generate_consultation(
    saju: dict,
    rag_ctx: dict,
    question: str,
    category: str = "general",
    provider: str | None = None,
) -> ConsultationOutput:
    """
    한줄 상담 LLM 호출 — ConsultationOutput(headline, content) 반환.
    """
    llm = get_llm(provider)

    parser: PydanticOutputParser[ConsultationOutput] = PydanticOutputParser(
        pydantic_object=ConsultationOutput
    )
    format_instructions = parser.get_format_instructions()

    user_text = format_question_message(saju, rag_ctx, question, category, format_instructions)
    messages = [
        SystemMessage(content=QUESTION_SYSTEM_PROMPT),
        HumanMessage(content=user_text),
    ]

    try:
        response = await llm.ainvoke(messages)
        raw = response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        logger.error("Consultation LLM 호출 실패: %s", exc)
        raise

    try:
        return parser.parse(raw)
    except Exception as parse_exc:
        logger.warning("Consultation 1차 파싱 실패, 재시도: %s", parse_exc)
        try:
            fix_messages = [
                SystemMessage(content="You are a JSON fixer. Return only valid JSON."),
                HumanMessage(content=(
                    f"Fix to match schema:\n{format_instructions}\n\n"
                    f"Original:\n{raw}\n\nReturn ONLY fixed JSON."
                )),
            ]
            fix_response = await get_llm(provider).ainvoke(fix_messages)
            fix_raw = fix_response.content if hasattr(fix_response, "content") else str(fix_response)
            return parser.parse(fix_raw)
        except Exception as fix_exc:
            logger.error("Consultation 파싱 최종 실패: %s", fix_exc)
            raise RuntimeError(f"Consultation 파싱 실패: {fix_exc}") from fix_exc
```

**주의**: `writer.py` 상단 import에 `from schemas.question import ConsultationOutput` 추가 필요.
`from llm.prompts import ...` 라인을 `QUESTION_SYSTEM_PROMPT, format_question_message` 포함으로 업데이트.

- [ ] **Step 3: 문법 검증**

```bash
cd backend && python3 -c "
from llm.prompts import QUESTION_SYSTEM_PROMPT, format_question_message
from schemas.question import ConsultationOutput
print('prompts OK')
print('schema OK')
"
```
Expected: 두 줄 모두 OK

- [ ] **Step 4: Commit**

```bash
git add backend/llm/prompts.py backend/llm/writer.py
git commit -m "feat: add question system prompt and generate_consultation writer"
```

---

### Task 4: Router + main.py

**Files:**
- Create: `backend/routers/question.py`
- Modify: `backend/main.py`

- [ ] **Step 1: 라우터 생성**

```python
"""한줄 상담 API 라우터."""

from __future__ import annotations
from fastapi import APIRouter
from schemas.question import QuestionRequest, QuestionResponse
from core.errors import SWAGGER_ERRORS
from core.exceptions import CalcFailedException
from llm.pipelines.question import run_question_consultation

router = APIRouter(prefix="/api/question", tags=["한줄 상담"])


@router.post(
    "",
    response_model=QuestionResponse,
    summary="한줄 상담",
    description="""
생년월일시 + 고민(10~200자) + 카테고리를 입력하면 사주 기반 AI 단답형 상담을 반환합니다.

**처리 흐름**:
1. 사주 계산 (Engine)
2. 고민 + 카테고리 + 사주 키워드 기반 RAG 검색
3. 용신/기신 기반 Reranking (일반론 억제)
4. Chain-of-Thought Writer (headline + content)

**카테고리**: career(직업) / love(연애) / money(재물) / health(건강) / general(일반)
""",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def ask_question(req: QuestionRequest) -> QuestionResponse:
    try:
        result = await run_question_consultation(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
            question=req.question,
            category=req.category,
        )
        return QuestionResponse(
            headline=result["headline"],
            content=result["content"],
            category=req.category,
        )
    except Exception as exc:
        raise CalcFailedException(str(exc)) from exc
```

- [ ] **Step 2: `main.py` 라우터 등록**

`main.py`에서:
```python
# app.include_router(question.router)        # 구현 예정
```
→
```python
app.include_router(question.router)
```
그리고 상단 import 줄을 확장:
```python
# 기존: from routers import saju, cities, auth, profiles, share
# 변경: question 추가
from routers import saju, cities, auth, profiles, share, question
```
별도 `from routers import question` 라인을 새로 추가하지 말 것.

- [ ] **Step 3: 서버 시작 확인**

```bash
cd backend && python3 -c "from routers.question import router; print('router OK')"
```
Expected: `router OK`

- [ ] **Step 4: Commit**

```bash
git add backend/routers/question.py backend/main.py
git commit -m "feat: add POST /api/question endpoint"
```

---

## Chunk 2: 프론트엔드 — Types + Composable + Page

### Task 5: Types (`frontend/types/saju.ts`)

**Files:**
- Modify: `frontend/types/saju.ts`

- [ ] **Step 1: 타입 추가**

`saju.ts` 파일 끝에 추가:

```typescript
// ── 한줄 상담 ────────────────────────────────────────────────────────────────

export type QuestionCategory = 'career' | 'love' | 'money' | 'health' | 'general'

export interface QuestionRequest extends SajuCalcRequest {
  question: string
  category: QuestionCategory
}

export interface ConsultationResponse {
  headline: string
  content: string
  category: string
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/types/saju.ts
git commit -m "feat: add QuestionRequest and ConsultationResponse types"
```

---

### Task 6: Composable (`frontend/composables/useSajuApi.ts`)

**Files:**
- Modify: `frontend/composables/useSajuApi.ts`

- [ ] **Step 1: `askQuestion()` 추가**

import 라인에 `QuestionRequest, ConsultationResponse` 추가.
반환 객체에 `askQuestion` 추가:

```typescript
import type { ..., QuestionRequest, ConsultationResponse } from '~/types/saju'

// ... 기존 함수들 ...

async function askQuestion(req: QuestionRequest): Promise<ConsultationResponse> {
  return $fetch<ConsultationResponse>(`${base}/api/question`, {
    method: 'POST',
    body: req,
  })
}

return { calcSaju, getWolUn, getYeonUn, getIlJin, getDailyFortune,
         createDailyShare, getDailyShareInput, askQuestion }
```

- [ ] **Step 2: Commit**

```bash
git add frontend/composables/useSajuApi.ts
git commit -m "feat: add askQuestion composable function"
```

---

### Task 7: Page (`frontend/pages/question/index.vue`)

**Files:**
- Create: `frontend/pages/question/index.vue`

스텝: `select` → `input` / `profile` → `question` → `result`
`daily/index.vue` 구조 그대로 따르되, step 3을 고민 입력으로 교체.

- [ ] **Step 1: 페이지 생성**

```vue
<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import type { SajuCalcRequest, ConsultationResponse, QuestionCategory } from '~/types/saju'
import { STORAGE_KEYS } from '~/utils/storageKeys'

const auth   = useAuthStore()
const config = useRuntimeConfig()
const base   = config.public.apiBase
const { askQuestion } = useSajuApi()
const goToLogin = useGoToLogin()

// ── 상태 ─────────────────────────────────────────────────────────────────────
type Step = 'select' | 'input' | 'profile' | 'question' | 'result'

interface ProfileItem {
  id: number; name: string; birth_date: string; birth_time: string | null
  calendar: string; gender: string; is_leap_month: boolean
  day_stem: string | null; day_stem_element: string | null
}

const CATEGORY_LABELS: Record<QuestionCategory, string> = {
  career: '직업·이직',
  love:   '연애·결혼',
  money:  '재물·투자',
  health: '건강',
  general: '기타',
}

const step             = ref<Step>('select')
const loading          = ref(false)
const error            = ref('')
const result           = ref<ConsultationResponse | null>(null)
const profiles         = ref<ProfileItem[]>([])
const profLoad         = ref(false)
const showLoginDialog  = ref(false)
const pendingBirthInput = ref<SajuCalcRequest | null>(null)
const pendingName      = ref('')

// 고민 입력
const question   = ref('')
const category   = ref<QuestionCategory>('general')
const CHAR_MIN   = 10
const CHAR_MAX   = 200
const questionValid = computed(
  () => question.value.length >= CHAR_MIN && question.value.length <= CHAR_MAX
)

// ── 프로필 로드 ───────────────────────────────────────────────────────────────
async function loadProfiles() {
  if (!auth.isLoggedIn) return
  profLoad.value = true
  try {
    profiles.value = await auth.authFetch<ProfileItem[]>(`${base}/api/profiles`)
  } catch { profiles.value = [] }
  finally { profLoad.value = false }
}

function goProfile() {
  if (!auth.isLoggedIn) { showLoginDialog.value = true; return }
  loadProfiles()
  step.value = 'profile'
}

// ── 생년월일 확보 후 고민 입력 스텝으로 ──────────────────────────────────────
function onFormSubmit(req: SajuCalcRequest) {
  pendingBirthInput.value = req
  pendingName.value = req.name ?? ''
  step.value = 'question'
}

function onProfileSelect(p: ProfileItem) {
  pendingBirthInput.value = {
    birth_date:    p.birth_date,
    birth_time:    p.birth_time ?? undefined,
    gender:        p.gender as 'male' | 'female',
    calendar:      p.calendar as 'solar' | 'lunar',
    is_leap_month: p.is_leap_month,
  }
  pendingName.value = p.name
  step.value = 'question'
}

// ── 상담 실행 ──────────────────────────────────────────────────────────────
async function submitQuestion() {
  if (!pendingBirthInput.value || !questionValid.value) return
  loading.value = true
  error.value   = ''
  try {
    result.value = await askQuestion({
      ...pendingBirthInput.value,
      question: question.value,
      category: category.value,
    })
    step.value = 'result'
  } catch {
    error.value = '상담을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

function reset() {
  result.value           = null
  error.value            = ''
  question.value         = ''
  category.value         = 'general'
  pendingBirthInput.value = null
  pendingName.value      = ''
  step.value             = 'select'
}
</script>

<template>
  <div class="question-wrap">

    <!-- 헤더 -->
    <div class="q-header">
      <button class="back-btn" @click="
        step === 'select' ? navigateTo('/')
        : step === 'result' ? reset()
        : step === 'question' ? (step = 'select')
        : (step = 'select')
      ">
        <svg viewBox="0 0 24 24" fill="none" class="w-5 h-5">
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <div>
        <h1 class="q-title">
          <template v-if="step === 'result' && pendingName">{{ pendingName }}님의 상담 결과</template>
          <template v-else>한줄 상담</template>
        </h1>
        <p class="q-subtitle">사주를 바탕으로 고민에 답해드립니다</p>
      </div>
    </div>

    <!-- ── Step 1: 방법 선택 ── -->
    <div v-if="step === 'select'" class="select-wrap animate-fade-up">
      <div class="intro-card card">
        <p class="intro-text">생년월일을 알면 고민에 대한<br>사주 기반 답변을 드립니다.</p>
      </div>
      <div class="method-btns">
        <button class="btn-primary method-btn" @click="step = 'input'">직접 입력하기</button>
        <button class="method-btn-outline" @click="goProfile">저장된 만세력으로 보기</button>
      </div>
    </div>

    <!-- ── Step 2a: 직접 입력 ── -->
    <div v-else-if="step === 'input'" class="input-wrap animate-fade-up">
      <ClientOnly>
        <SajuInputForm submit-label="다음" @submit="onFormSubmit" />
      </ClientOnly>
    </div>

    <!-- ── Step 2b: 프로필 선택 ── -->
    <div v-else-if="step === 'profile'" class="profile-step animate-fade-up">
      <div v-if="profLoad" class="center-state"><LoadingSpinner size="sm" /></div>
      <div v-else-if="profiles.length === 0" class="card" style="text-align:center;padding:32px;">
        <p class="fs-body" style="color:var(--text-muted);">저장된 만세력이 없습니다.</p>
        <NuxtLink to="/profile" class="btn-primary" style="margin-top:16px;max-width:200px;margin-inline:auto;">
          만세력 보러가기
        </NuxtLink>
      </div>
      <div v-else class="profiles-list">
        <button
          v-for="p in profiles" :key="p.id"
          class="profile-card-item"
          :disabled="loading"
          @click="onProfileSelect(p)"
        >
          <div class="profile-card-inner">
            <div class="profile-info">
              <p class="profile-name">{{ p.name }}</p>
              <p class="profile-birth">
                {{ p.birth_date.replace(/-/g, '.') }} · {{ p.gender === 'male' ? '남' : '여' }}
              </p>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- ── Step 3: 고민 입력 ── -->
    <div v-else-if="step === 'question'" class="question-step animate-fade-up">
      <p class="q-guide fs-sub">
        <strong>{{ pendingName || '나' }}</strong>의 고민을 입력해 주세요.
      </p>

      <!-- 카테고리 칩 -->
      <div class="category-chips">
        <button
          v-for="(label, cat) in CATEGORY_LABELS"
          :key="cat"
          class="cat-chip"
          :class="{ active: category === cat }"
          @click="category = cat as QuestionCategory"
        >{{ label }}</button>
      </div>

      <!-- 고민 textarea -->
      <div class="textarea-wrap">
        <textarea
          v-model="question"
          class="question-textarea"
          :placeholder="`예: 올해 이직 운이 있을까요?\n예: 지금 만나는 사람과 궁합이 어떨까요?`"
          :maxlength="CHAR_MAX"
          rows="4"
        />
        <span
          class="char-count fs-tiny"
          :class="{ warn: question.length < CHAR_MIN && question.length > 0, ok: questionValid }"
        >{{ question.length }} / {{ CHAR_MAX }}</span>
      </div>
      <p v-if="question.length > 0 && question.length < CHAR_MIN" class="hint-text fs-tiny">
        최소 {{ CHAR_MIN }}자 이상 입력해 주세요.
      </p>

      <p v-if="error" class="error-msg fs-label">{{ error }}</p>

      <button
        class="btn-primary submit-btn"
        :disabled="!questionValid || loading"
        @click="submitQuestion"
      >
        <LoadingSpinner v-if="loading" size="sm" />
        <span v-else>상담 받기</span>
      </button>
    </div>

    <!-- ── Step 4: 결과 ── -->
    <div v-else-if="step === 'result' && result" class="result-wrap animate-fade-up">
      <div class="result-card card">
        <p class="result-category fs-tiny">{{ CATEGORY_LABELS[result.category as QuestionCategory] ?? result.category }}</p>
        <h2 class="result-headline">{{ result.headline }}</h2>
        <p class="result-content">{{ result.content }}</p>
      </div>
      <div class="result-question-echo card" style="padding:14px 18px;">
        <p class="fs-tiny" style="color:var(--text-muted);">입력한 고민</p>
        <p class="fs-sub" style="color:var(--text-secondary);margin-top:4px;">{{ question }}</p>
      </div>
      <button class="btn-secondary" @click="reset">다른 고민 상담하기</button>
    </div>

  </div>

  <!-- 로그인 유도 -->
  <AppDialog
    v-model:show="showLoginDialog"
    title="로그인이 필요해요"
    desc="저장된 만세력은 로그인 후 이용할 수 있어요."
    cancel-text="취소"
  >
    <button class="btn-primary" style="width:100%" @click="goToLogin()">로그인하러 가기</button>
  </AppDialog>
</template>

<style scoped>
.question-wrap {
  max-width: 480px;
  margin: 0 auto;
  padding: 12px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.q-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding-top: 8px;
}
.back-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--surface-1);
  color: var(--text-secondary);
  flex-shrink: 0; margin-top: 2px; cursor: pointer;
  transition: background 0.15s;
}
.back-btn:hover { background: var(--surface-2); }
.q-title {
  font-size: 22px; font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em; line-height: 1.2;
}
.q-subtitle { font-size: var(--fs-sub); color: var(--text-muted); margin-top: 3px; }

/* Step1 */
.select-wrap { display: flex; flex-direction: column; gap: 14px; }
.intro-card { padding: 24px; text-align: center; }
.intro-text { font-size: var(--fs-body); color: var(--text-secondary); line-height: 1.7; }
.method-btns { display: flex; flex-direction: column; gap: 10px; }
.method-btn {
  width: 100%; padding: 15px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px; cursor: pointer;
}
.method-btn-outline {
  width: 100%; padding: 14px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px;
  border: 2px solid var(--accent); background: transparent;
  color: var(--accent); cursor: pointer; transition: background 0.15s;
}
.method-btn-outline:hover { background: color-mix(in srgb, var(--accent) 8%, transparent); }

/* Step2b */
.center-state { min-height: 200px; display: flex; align-items: center; justify-content: center; }
.profile-step { display: flex; flex-direction: column; gap: 10px; }
.profiles-list { display: flex; flex-direction: column; gap: 10px; }
.profile-card-item {
  border-radius: 16px; border: 1px solid var(--border-default);
  background: var(--surface-1); width: 100%; text-align: left;
  cursor: pointer; transition: background 0.15s;
}
.profile-card-item:hover:not(:disabled) { background: var(--surface-2); }
.profile-card-inner { padding: 18px 20px; }
.profile-name { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.profile-birth { font-size: var(--fs-sub); color: var(--text-muted); margin-top: 4px; }

/* Step3 — 고민 입력 */
.question-step { display: flex; flex-direction: column; gap: 12px; }
.q-guide { color: var(--text-muted); }
.category-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.cat-chip {
  padding: 6px 14px; border-radius: 20px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-label); font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.cat-chip.active {
  border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
}
.textarea-wrap { position: relative; }
.question-textarea {
  width: 100%; min-height: 100px; padding: 14px 16px;
  border-radius: 12px; border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-primary);
  font-size: var(--fs-body); font-family: inherit; resize: vertical;
  transition: border-color 0.15s; box-sizing: border-box;
}
.question-textarea:focus { outline: none; border-color: var(--accent); }
.char-count {
  position: absolute; bottom: 10px; right: 14px;
  color: var(--text-muted);
}
.char-count.warn { color: var(--color-bad); }
.char-count.ok   { color: var(--text-muted); }
.hint-text { color: var(--text-muted); padding: 0 4px; }
.submit-btn {
  width: 100%; padding: 15px; font-size: var(--fs-body);
  font-weight: 700; border-radius: 12px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.error-msg { color: var(--color-bad); font-weight: 600; }

/* Step4 — 결과 */
.result-wrap { display: flex; flex-direction: column; gap: 12px; }
.result-card { padding: 28px 24px; display: flex; flex-direction: column; gap: 12px; }
.result-category {
  color: var(--accent); font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em;
}
.result-headline {
  font-size: 20px; font-weight: 800; color: var(--text-primary);
  line-height: 1.4; letter-spacing: -0.02em;
}
.result-content {
  font-size: var(--fs-body); color: var(--text-secondary);
  line-height: 1.75; white-space: pre-wrap;
}
.btn-secondary {
  width: 100%; padding: 12px; border-radius: 10px;
  border: 1px solid var(--border-default);
  background: var(--surface-1); color: var(--text-secondary);
  font-size: var(--fs-body); font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.btn-secondary:hover { background: var(--surface-2); }

@media (min-width: 768px) {
  .question-wrap { max-width: 960px; padding: 32px 40px 60px; }
}
</style>
```

- [ ] **Step 2: 홈 화면에 한줄 상담 카드 추가 (optional)**

`pages/index.vue` 서비스 카드 영역에 한줄 상담 진입 링크 추가 (오늘의 운세 카드 옆).

- [ ] **Step 3: Commit**

```bash
git add frontend/pages/question/index.vue frontend/composables/useSajuApi.ts frontend/types/saju.ts
git commit -m "feat: add question consultation page with category chips and char counter"
```

---

## 검증 체크리스트

```bash
# 백엔드 — Reranking 단위 테스트
cd backend && python3 -m pytest tests/test_question_pipeline.py -v

# 문법 검사
python3 -c "
from schemas.question import QuestionRequest, ConsultationOutput
from llm.prompts import QUESTION_SYSTEM_PROMPT, format_question_message
from llm.writer import generate_consultation
from routers.question import router
print('ALL OK')
"

# API 엔드포인트 확인 (서버 실행 중일 때)
curl -X POST http://localhost:8000/api/question \
  -H 'Content-Type: application/json' \
  -d '{
    "birth_date": "1990-03-15",
    "birth_time": "14:30",
    "gender": "male",
    "calendar": "solar",
    "question": "올해 이직 운이 있을까요?",
    "category": "career"
  }'
```

Expected 응답:
```json
{
  "headline": "정관격의 책임감이 지금 당신을 더 큰 무대로 부르고 있습니다",
  "content": "...",
  "category": "career"
}
```
