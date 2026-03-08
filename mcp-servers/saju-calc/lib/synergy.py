"""
Pattern ↔ Dynamics 시너지 태그 연산.

saju-calc가 패턴과 동역학을 각각 감지한 후,
두 정보가 만나는 지점에서 추가 해석 힌트(synergy_tags)를 생성한다.

설계 원칙:
  - Deterministic: LLM 없이 규칙 기반으로 생성
  - 경량: pattern_id + dynamics_key 조합 룩업 테이블
  - 확장 용이: SYNERGY_MAP에 항목만 추가하면 됨
"""

from __future__ import annotations


# ─── 시너지 룩업 테이블 ──────────────────────────────────────────
# key: (pattern_id, dynamics_trigger_key)
# dynamics_trigger_key: "stem_hap:{name}" | "branch:{relation}" | "rooting:{level}" | "flow:{smooth}"

SYNERGY_MAP: dict[tuple[str, str], list[str]] = {
    # 천간합 × 패턴
    ("sig_sang_saeng_jae",  "stem_hap:갑기합"): ["idea_grounded_in_reality",    "concept_to_durable_profit"],
    ("sig_sang_saeng_jae",  "stem_hap:을경합"): ["precise_creative_income",      "quality_driven_monetization"],
    ("sig_sang_saeng_jae",  "stem_hap:병신합"): ["strategic_creative_income",    "data_backed_expression"],
    ("sig_sang_saeng_jae",  "stem_hap:정임합"): ["empathetic_creative_income",   "storytelling_wealth"],
    ("sig_sang_saeng_jae",  "stem_hap:무계합"): ["mystical_creative_income",     "intuitive_monetization"],
    ("gun_gyeop_jaeng_jae", "stem_hap:갑기합"): ["independent_but_anchored",     "solo_with_solid_base"],
    ("sang_gwan_pae_in",    "stem_hap:을경합"): ["sharp_yet_diplomatic",         "principled_critique"],
    ("sang_gwan_pae_in",    "stem_hap:정임합"): ["heart_sharpened_by_wisdom",    "emotional_intellectual_critique"],
    ("sig_sin_je_sal",      "stem_hap:병신합"): ["analytical_humor_defense",     "calculated_resilience"],
    ("sig_sin_je_sal",      "stem_hap:무계합"): ["charismatic_resilience",       "presence_vs_pressure"],
    ("gwan_in_sang_saeng",  "stem_hap:정임합"): ["empathetic_institutional_growth", "people_centered_career"],

    # 지지 관계 × 패턴
    ("sig_sang_saeng_jae",  "branch:sam_hap"): ["elemental_creative_force",     "concentrated_income_stream"],
    ("sig_sang_saeng_jae",  "branch:yuk_hap"): ["harmonious_creative_flow",     "smooth_idea_to_money"],
    ("gun_gyeop_jaeng_jae", "branch:chung"):   ["turbulent_rivalry",            "unstable_competition"],
    ("sig_sin_je_sal",      "branch:chung"):   ["pressure_amplified_crisis",    "forced_creative_solution"],
    ("sig_sin_je_sal",      "branch:hyung"):   ["forged_under_pressure",        "crisis_mastery_amplified"],
    ("sang_gwan_pae_in",    "branch:hyung"):   ["battle_hardened_critic",       "sharpness_from_adversity"],
    ("jae_da_sin_yak",      "branch:hae"):     ["blocked_opportunities",        "wealth_access_hindered"],
    ("gun_gyeop_jaeng_jae", "branch:hae"):     ["rivalry_with_betrayal",        "sabotaged_competition"],
    ("gwan_in_sang_saeng",  "branch:sam_hap"): ["institutional_powerhouse",     "systematic_mastery"],
    ("gwan_in_sang_saeng",  "branch:yuk_hap"): ["harmonious_institution_fit",   "effortless_promotion"],
    ("jae_da_sin_yak",      "branch:yuk_hap"): ["opportunity_flows_naturally",  "less_struggle_for_wealth"],

    # 통근 강약 × 패턴
    ("sig_sang_saeng_jae",  "rooting:strong"): ["unstoppable_creative_engine",  "self_powered_income"],
    ("gun_gyeop_jaeng_jae", "rooting:strong"): ["dominant_rival",               "strongest_in_competition"],
    ("jae_da_sin_yak",      "rooting:weak"):   ["overwhelmed_by_opportunity",   "critical_energy_crisis"],
    ("gwan_in_sang_saeng",  "rooting:weak"):   ["dependent_on_institution",     "needs_external_support"],

    # 오행 흐름 × 패턴
    ("sig_sang_saeng_jae",  "flow:smooth"): ["frictionless_creative_wealth",   "smooth_income_generation"],
    ("gwan_in_sang_saeng",  "flow:smooth"): ["effortless_institutional_climb", "natural_promotion_flow"],
    ("sig_sin_je_sal",      "flow:conflict"): ["maximum_pressure_maximum_creativity", "crisis_as_fuel"],
    ("gun_gyeop_jaeng_jae", "flow:conflict"): ["fierce_battle_ground",         "war_of_attrition"],
}


# ─── Dynamics 키 추출 ────────────────────────────────────────────

def _extract_dynamics_keys(dynamics: dict) -> list[str]:
    """
    build_dynamics() 결과에서 시너지 룩업용 키 목록 추출.

    Returns: ["stem_hap:갑기합", "branch:chung", "rooting:strong", "flow:smooth", ...]
    """
    keys: list[str] = []

    for hap in dynamics.get("stem_hap", []):
        keys.append(f"stem_hap:{hap['name']}")

    for rel in dynamics.get("active_relations", []):
        keys.append(f"branch:{rel['type']}")

    rooting = dynamics.get("rooting_map", {})
    level = rooting.get("strength_level", "none")
    if level in ("very_strong", "strong"):
        keys.append("rooting:strong")
    elif level in ("none", "moderate"):
        keys.append("rooting:weak")

    flow = dynamics.get("energy_flow", {})
    if flow.get("is_smooth"):
        keys.append("flow:smooth")
    else:
        keys.append("flow:conflict")

    return keys


# ─── 공개 API ───────────────────────────────────────────────────

def compute_synergy_tags(
    structure_patterns: list[dict],
    dynamics: dict,
) -> list[dict]:
    """
    구조 패턴 목록 + 동역학 결과 → 시너지 태그 목록 반환.

    Args:
        structure_patterns : detect_structure_patterns()의 결과
        dynamics           : build_dynamics()의 결과

    Returns:
        [
          {
            "pattern_id"   : "sig_sang_saeng_jae",
            "dynamics_key" : "stem_hap:갑기합",
            "synergy_tags" : ["idea_grounded_in_reality", ...]
          },
          ...
        ]
        중복 없이 반환. Writer Agent는 이 태그를 추가 해석 힌트로 활용.
    """
    pattern_ids = {p["id"] for p in structure_patterns}
    dyn_keys    = _extract_dynamics_keys(dynamics)

    results: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for pid in pattern_ids:
        for dkey in dyn_keys:
            combo = (pid, dkey)
            if combo in seen:
                continue
            tags = SYNERGY_MAP.get(combo)
            if tags:
                results.append({
                    "pattern_id":   pid,
                    "dynamics_key": dkey,
                    "synergy_tags": tags,
                })
                seen.add(combo)

    return results
