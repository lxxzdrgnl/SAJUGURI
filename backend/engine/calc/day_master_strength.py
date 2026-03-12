"""
일간(日干) 강약 점수화.

판단 기준:
  1. 월령 득실 (±40) — 가장 중요
  2. 비겁 개수   (±25)
  3. 인성 개수   (+20)
  4. 재관식상    (−15)
"""

from __future__ import annotations
from engine.data.earthly_branches import BRANCHES_BY_KOREAN
from engine.data.wuxing import WUXING_GENERATION

_SUPPORT_GODS: set[str] = {"비견", "겁재", "정인", "편인"}

_LEVEL_8_THRESHOLDS = [
    (90, "극왕"), (80, "태강"), (70, "신강"), (60, "중화신강"),
    (50, "중화신약"), (40, "신약"), (30, "태약"),
]


def _get_level_8(score: int) -> str:
    for threshold, label in _LEVEL_8_THRESHOLDS:
        if score >= threshold:
            return label
    return "극약"


# 월지(月支)와 일간(日干) 오행의 관계 → 월령 득실
def _month_branch_relation(day_element: str, month_branch: str) -> str:
    """월지 오행이 일간을 생하면 strong, 극하면 weak, 그 외 medium."""
    branch_el = BRANCHES_BY_KOREAN[month_branch]["element"]
    if WUXING_GENERATION.get(branch_el) == day_element:
        return "strong"
    # 일간이 극하는 오행이 월지에 있으면 weak (재성이 강한 달)
    from engine.data.wuxing import WUXING_DESTRUCTION
    if WUXING_DESTRUCTION.get(day_element) == branch_el:
        return "weak"
    if branch_el == day_element:
        return "strong"
    return "medium"


def _branch_ten_god_category(day_stem: str, branch: str) -> str:
    """지지 정기(正氣) 기준 십성 반환."""
    from engine.calc.ten_gods import get_branch_ten_god
    return get_branch_ten_god(day_stem, branch)


def analyze_day_master_strength(saju: dict, ten_gods_dist: dict) -> dict:
    """
    일간 강약 종합 분석.

    Returns:
        level: very_strong | strong | medium | weak | very_weak
        score: 0-100
        analysis: 이유 문자열
    """
    score = 50
    reasons: list[str] = []
    factors: dict[str, int] = {}

    day_element = saju["day_pillar"]["stem_element"]
    month_branch = saju["month_pillar"]["branch"]

    # 1. 월령 득실 (±30)
    wol_relation = _month_branch_relation(day_element, month_branch)
    if wol_relation == "strong":
        score += 15; factors["wol_ryeong"] = 15
        reasons.append("월령을 득하여 강함")
    elif wol_relation == "medium":
        score += 5;  factors["wol_ryeong"] = 5
        reasons.append("월령 중립")
    else:
        score -= 20; factors["wol_ryeong"] = -20
        reasons.append("월령을 실하여 약함")

    # 2. 비겁 (±22)
    bigeop = ten_gods_dist.get("비견", 0) + ten_gods_dist.get("겁재", 0)
    if bigeop >= 4:
        score += 22; factors["bigeop"] = 22;  reasons.append("비겁 과다")
    elif bigeop >= 2:
        score += 12; factors["bigeop"] = 12;  reasons.append("비겁 적절")
    elif bigeop >= 1:
        score += 5;  factors["bigeop"] = 5;   reasons.append("비겁 소량")
    elif bigeop >= 0.5:
        factors["bigeop"] = 0;               reasons.append("비겁 극소 (지지만)")
    else:
        score -= 10; factors["bigeop"] = -10; reasons.append("비겁 없음")

    # 3. 인성 (+18)
    inseong = ten_gods_dist.get("정인", 0) + ten_gods_dist.get("편인", 0)
    if inseong >= 3:
        score += 18; factors["inseong"] = 18; reasons.append("인성 과다")
    elif inseong >= 2:
        score += 8;  factors["inseong"] = 8;  reasons.append("인성 적절")
    elif inseong >= 1:
        score += 5;  factors["inseong"] = 5;  reasons.append("인성 소량")
    else:
        factors["inseong"] = 0

    # 4. 재관식상 (설기, −22)
    seolgi = sum(ten_gods_dist.get(g, 0) for g in
                 ["정재", "편재", "정관", "편관", "식신", "상관"])
    if seolgi >= 6:
        score -= 22; factors["seolgi"] = -22; reasons.append("재관식상 과다")
    elif seolgi >= 4:
        score -= 18; factors["seolgi"] = -18; reasons.append("재관식상 많음")
    elif seolgi >= 2:
        score -= 5;  factors["seolgi"] = -5;  reasons.append("재관식상 있음")
    else:
        factors["seolgi"] = 0

    raw_score = score
    score = max(0, min(100, score))

    if score >= 80:   level = "very_strong"
    elif score >= 65: level = "strong"
    elif score >= 40: level = "medium"
    elif score >= 25: level = "weak"
    else:             level = "very_weak"

    # ── 득령/득지/득시/득세 ──────────────────────────────────────
    day_stem   = saju["day_pillar"]["stem"]
    day_branch = saju["day_pillar"]["branch"]

    deuk_ryeong = wol_relation == "strong"
    deuk_ji  = _branch_ten_god_category(day_stem, day_branch) in _SUPPORT_GODS
    if saju.get("hour_pillar") is not None:
        hour_branch = saju["hour_pillar"]["branch"]
        deuk_si = _branch_ten_god_category(day_stem, hour_branch) in _SUPPORT_GODS
    else:
        deuk_si = False  # 시주 미입력 시 득시 판단 불가

    supporting = bigeop + inseong
    opposing   = seolgi
    deuk_se    = supporting > opposing

    return {
        "level": level,
        "level_8": _get_level_8(score),
        "score": score,
        "raw_score": raw_score,
        "score_range": [0, 100],
        "factors": factors,
        "analysis": ". ".join(reasons),
        "wol_ryeong": wol_relation,
        "deuk_ryeong": deuk_ryeong,
        "deuk_ji":     deuk_ji,
        "deuk_si":     deuk_si,
        "deuk_se":     deuk_se,
    }
