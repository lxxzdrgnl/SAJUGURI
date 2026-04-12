"""
RAG 청크 Reranking + 쿼리 빌더.

용신/기신 오행 기반 점수 조정으로 사주에 맞는 지식을 우선 노출.
question 파이프라인과 (추후) chat 파이프라인이 공유.
"""

from __future__ import annotations


# ─── 오행 키워드 매핑 ─────────────────────────────────────────────────────────

ELEMENT_KEYWORDS: dict[str, list[str]] = {
    "목": ["목", "木", "갑", "을", "인", "묘"],
    "화": ["화", "火", "병", "정", "사", "오"],
    "토": ["토", "土", "무", "기", "진", "술", "축", "미"],
    "금": ["금", "金", "경", "신", "유"],
    "수": ["수", "水", "임", "계", "자", "해"],
}


# ─── 카테고리 → RAG 힌트 키워드 ───────────────────────────────────────────────

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


def build_question_query(question: str, category: str, core_keywords: list[str]) -> str:
    """
    RAG 검색용 쿼리 문자열 조립.
    question + category 힌트 + core_keywords 최대 3개
    """
    parts = [question]
    if hint := CATEGORY_QUERY_HINT.get(category, ""):
        parts.append(hint)
    parts.extend(core_keywords[:3])
    return " ".join(filter(None, parts))


def rerank_chunks(
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
