"""
Behavior Synthesizer — 십성 분포 → 행동 프로파일 합성.

Pipeline: energy_profile + ten_gods distribution → behavior_profile

설계 원칙:
  - 십성 strength(%) 기반 가중 투표로 behavior_vector 우선순위 결정
  - 벡터 위치 가중치: [1.0, 0.8, 0.6, 0.5] (앞쪽 벡터가 핵심 행동)
  - 동일 태그가 여러 십성에서 등장하면 점수 누적 (공통 행동 강화)
  - Deterministic: LLM 없이 규칙 기반
"""

from __future__ import annotations


# 십성 → behavior_vector 매핑 테이블
# ten_gods.json의 behavior_vector 필드와 동기화 유지
_TEN_GOD_BEHAVIOR_MAP: dict[str, list[str]] = {
    "비견": ["self_reliance", "competitive_drive", "peer_solidarity", "stubborn_independence"],
    "겁재": ["aggressive_ambition", "fast_risk_taking", "charismatic_leadership", "impulsive_action"],
    "식신": ["creative_expression", "optimistic_enjoyment", "nurturing_generosity", "talent_monetization"],
    "상관": ["critical_analysis", "creative_rebellion", "sharp_expression", "authority_questioning"],
    "편재": ["opportunistic_action", "resource_mobilization", "risk_taking", "social_networking"],
    "정재": ["diligent_accumulation", "financial_discipline", "risk_aversion", "steady_reliability"],
    "편관": ["pressure_activation", "results_at_all_costs", "crisis_leadership", "uncompromising_drive"],
    "정관": ["rule_adherence", "responsibility_acceptance", "structure_maintenance", "honor_seeking"],
    "편인": ["unconventional_intuition", "independent_learning", "pattern_recognition", "mystical_depth"],
    "정인": ["scholarly_pursuit", "methodical_learning", "nurturing_protection", "credential_seeking"],
}

# 벡터 위치 가중치 (첫 번째 벡터가 핵심 행동)
_POSITION_WEIGHTS = [1.0, 0.8, 0.6, 0.5]


def synthesize_behavior_profile(
    ten_gods_dist: dict[str, float],
    top_n: int = 6,
) -> list[str]:
    """
    십성 분포(%) → 행동 프로파일(ranked list).

    Args:
        ten_gods_dist : {"편재": 30.0, "정관": 20.0, ...}
                        (0 제거된 퍼센트 분포 — calculate_saju의 ten_gods_dist_filtered)
        top_n         : 반환할 상위 behavior_tag 수 (default: 6)

    Returns:
        ["opportunistic_action", "risk_taking", "social_networking", ...]
        강도 높은 십성의 벡터가 앞에 위치
    """
    scores: dict[str, float] = {}

    for god_name, strength_pct in ten_gods_dist.items():
        vectors = _TEN_GOD_BEHAVIOR_MAP.get(god_name, [])
        for i, tag in enumerate(vectors):
            w = _POSITION_WEIGHTS[i] if i < len(_POSITION_WEIGHTS) else 0.4
            scores[tag] = scores.get(tag, 0.0) + strength_pct * w

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [tag for tag, _ in ranked[:top_n]]
