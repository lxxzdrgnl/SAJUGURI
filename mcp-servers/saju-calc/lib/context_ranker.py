"""
Context Ranking Layer — 분석 결과 우선순위화.

Calc Engine의 마지막 post-processing 단계:
패턴 / 신살 중 Writer에게 전달할 핵심 컨텍스트를 선별.

랭킹 기준 (4가지):
  1. priority    — 각 항목의 기본 중요도 (int 또는 str → int 변환)
  2. rarity      — 희귀 구조 보너스 (종격·특수살)
  3. interaction — synergy 교차 횟수 (패턴 간 상호작용이 많을수록 ↑)
  4. category    — 관성/재성 카테고리 우선 보정 (Writer 해석 중요도)
"""

from __future__ import annotations


# 희귀 구조 보너스
_RARE_PATTERN_BONUS: dict[str, int] = {
    "jong_wang":  20,
    "jong_jae":   20,
    "jong_sal":   20,
}

_RARE_SINSAL_BONUS: dict[str, int] = {
    "백호대살": 15,
    "양인살":   10,
    "괴강살":   10,
    "귀문관살": 8,
}

# 신살 priority 문자열 → 숫자 변환
_SINSAL_PRIORITY_MAP: dict[str, int] = {
    "high":    75,
    "medium":  55,
    "low":     35,
}


def rank_context(
    patterns: list[dict],
    sin_sals: list[dict],
    synergy: list[dict] | None = None,
    primary_n: int = 3,
    secondary_n: int = 2,
) -> dict:
    """
    패턴 + 신살 → 우선순위 컨텍스트 분류.

    Args:
        patterns   : detect_structure_patterns() 결과
        sin_sals   : find_sin_sals() + priority 태그 결과
        synergy    : compute_synergy_tags() 결과 (interaction 보너스용)
        primary_n  : primary_context 최대 항목 수 (default: 3)
        secondary_n: secondary_context 최대 항목 수 (default: 2)

    Returns:
        {
          "primary_context":   [{"id": ..., "type": ..., "score": ...}, ...],
          "secondary_context": [...]
        }
    """
    scored: list[tuple[str, str, float]] = []  # (id, type, score)

    # synergy에서 pattern별 interaction 횟수 집계
    interaction_count: dict[str, int] = {}
    for s in (synergy or []):
        pid = s.get("pattern_id", "")
        if pid:
            interaction_count[pid] = interaction_count.get(pid, 0) + 1

    # 패턴 점수화
    for p in patterns:
        pid   = p.get("id", "")
        base  = float(p.get("priority", 50))
        rare  = float(_RARE_PATTERN_BONUS.get(pid, 0))
        inter = float(interaction_count.get(pid, 0) * 5)
        scored.append((pid, "pattern", base + rare + inter))

    # 신살 점수화
    for s in sin_sals:
        sid = s.get("name", s.get("id", ""))
        raw = s.get("priority", "low")
        base = float(raw) if isinstance(raw, (int, float)) else float(_SINSAL_PRIORITY_MAP.get(str(raw), 35))
        rare = float(_RARE_SINSAL_BONUS.get(sid, 0))
        scored.append((sid, "sin_sal", base + rare))

    scored.sort(key=lambda x: x[2], reverse=True)

    primary = [
        {"id": sid, "type": stype, "score": round(score, 1)}
        for sid, stype, score in scored[:primary_n]
    ]
    secondary = [
        {"id": sid, "type": stype, "score": round(score, 1)}
        for sid, stype, score in scored[primary_n: primary_n + secondary_n]
    ]

    return {
        "primary_context":   primary,
        "secondary_context": secondary,
    }
