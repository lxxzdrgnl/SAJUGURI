"""
Life Domain Mapper — 행동 프로파일 → 생활 도메인별 해석 분류.

behavior_profile + context_ranking → 도메인별 핵심 태그 자동 매핑

4개 도메인:
  - career     : 직업·커리어 방향성
  - relationship: 연애·결혼·대인관계
  - wealth     : 재물·금전 흐름
  - personality: 성격·기질·강점

설계 원칙:
  - behavior_vector → domain 매핑 테이블 (Deterministic)
  - pattern/sin_sal 도메인 오버레이 (pattern_id → domain_hint)
  - 각 도메인 상위 3개 태그 선택
"""

from __future__ import annotations


# behavior_tag → 해당되는 도메인(들) 매핑
# 하나의 태그가 여러 도메인에 걸칠 수 있음
_BEHAVIOR_DOMAIN_MAP: dict[str, list[str]] = {
    # 비겁 계열
    "self_reliance":              ["career", "personality"],
    "competitive_drive":          ["career", "personality"],
    "peer_solidarity":            ["relationship", "career"],
    "stubborn_independence":      ["personality", "career"],
    "aggressive_ambition":        ["career", "wealth"],
    "fast_risk_taking":           ["wealth", "career"],
    "charismatic_leadership":     ["career", "relationship"],
    "impulsive_action":           ["personality", "wealth"],
    # 식상 계열
    "creative_expression":        ["career", "personality"],
    "optimistic_enjoyment":       ["personality", "relationship"],
    "nurturing_generosity":       ["relationship", "personality"],
    "talent_monetization":        ["wealth", "career"],
    "critical_analysis":          ["career", "personality"],
    "creative_rebellion":         ["career", "personality"],
    "sharp_expression":           ["career", "relationship"],
    "authority_questioning":      ["career", "personality"],
    # 재성 계열
    "opportunistic_action":       ["wealth", "career"],
    "resource_mobilization":      ["wealth", "career"],
    "risk_taking":                ["wealth", "personality"],
    "social_networking":          ["relationship", "career"],
    "diligent_accumulation":      ["wealth", "career"],
    "financial_discipline":       ["wealth", "personality"],
    "risk_aversion":              ["wealth", "personality"],
    "steady_reliability":         ["career", "relationship"],
    # 관성 계열
    "pressure_activation":        ["career", "personality"],
    "results_at_all_costs":       ["career", "wealth"],
    "crisis_leadership":          ["career", "personality"],
    "uncompromising_drive":       ["career", "personality"],
    "rule_adherence":             ["career", "personality"],
    "responsibility_acceptance":  ["career", "relationship"],
    "structure_maintenance":      ["career", "wealth"],
    "honor_seeking":              ["career", "relationship"],
    # 인성 계열
    "unconventional_intuition":   ["personality", "career"],
    "independent_learning":       ["career", "personality"],
    "pattern_recognition":        ["career", "personality"],
    "mystical_depth":             ["personality", "relationship"],
    "scholarly_pursuit":          ["career", "personality"],
    "methodical_learning":        ["career", "personality"],
    "nurturing_protection":       ["relationship", "personality"],
    "credential_seeking":         ["career", "wealth"],
}

# pattern → 도메인 힌트 오버레이
_PATTERN_DOMAIN_HINT: dict[str, dict[str, list[str]]] = {
    "sig_sang_saeng_jae":  {"wealth": ["creative_income", "talent_to_profit"],    "career": ["content_creator", "entrepreneur"]},
    "gwan_in_sang_saeng":  {"career": ["institutional_growth", "promotion_track"], "wealth": ["credential_income"]},
    "jae_da_sin_yak":      {"wealth": ["opportunity_overload", "need_focus"],      "personality": ["scattered_energy"]},
    "gun_gyeop_jaeng_jae": {"career": ["solo_better", "rivalry_pattern"],          "relationship": ["partnership_friction"]},
    "sig_sin_je_sal":      {"career": ["crisis_creative", "pressure_innovator"],   "personality": ["resilience_under_fire"]},
    "sang_gwan_pae_in":    {"career": ["intellectual_rebel", "evidence_critique"],  "personality": ["sharp_with_knowledge"]},
    "in_da_sin_gang":      {"career": ["theory_expert", "academia"],               "personality": ["action_deficit"]},
    "jong_wang":           {"personality": ["self_dominant", "independent_ruler"], "career": ["solo_or_leadership"]},
    "jong_jae":            {"wealth": ["wealth_dominant", "resource_controller"],  "career": ["business_or_finance"]},
    "jong_sal":            {"career": ["pressure_transcended", "extreme_focus"],   "personality": ["authority_surrender"]},
}

_DOMAINS = ("career", "relationship", "wealth", "personality")


def map_life_domains(
    behavior_profile: list[str],
    context_ranking: dict,
    top_per_domain: int = 3,
) -> dict[str, list[str]]:
    """
    행동 프로파일 + 컨텍스트 랭킹 → 도메인별 핵심 태그 매핑.

    Args:
        behavior_profile : synthesize_behavior_profile() 결과
        context_ranking  : rank_context() 결과
        top_per_domain   : 도메인당 반환할 최대 태그 수 (default: 3)

    Returns:
        {
          "career":       ["creative_expression", "talent_monetization", ...],
          "relationship": ["nurturing_generosity", "social_networking", ...],
          "wealth":       ["opportunistic_action", "creative_income", ...],
          "personality":  ["optimistic_enjoyment", "risk_taking", ...]
        }
    """
    # 도메인별 점수 누적
    domain_scores: dict[str, dict[str, float]] = {d: {} for d in _DOMAINS}

    # behavior_profile 가중 투표 (앞쪽 태그에 높은 가중치)
    for rank, tag in enumerate(behavior_profile):
        weight = max(1.0 - rank * 0.1, 0.3)
        for domain in _BEHAVIOR_DOMAIN_MAP.get(tag, []):
            domain_scores[domain][tag] = domain_scores[domain].get(tag, 0.0) + weight

    # primary/secondary context에서 pattern 도메인 힌트 오버레이
    all_context = context_ranking.get("primary_context", []) + context_ranking.get("secondary_context", [])
    for ctx in all_context:
        pid = ctx.get("id", "")
        score_bonus = ctx.get("score", 50.0) / 100.0  # 정규화
        hints = _PATTERN_DOMAIN_HINT.get(pid, {})
        for domain, tags in hints.items():
            if domain in domain_scores:
                for t in tags:
                    domain_scores[domain][t] = domain_scores[domain].get(t, 0.0) + score_bonus

    # 도메인별 상위 N개 선택
    result: dict[str, list[str]] = {}
    for domain in _DOMAINS:
        ranked = sorted(domain_scores[domain].items(), key=lambda x: x[1], reverse=True)
        result[domain] = [tag for tag, _ in ranked[:top_per_domain]]

    return result
