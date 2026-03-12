"""
십성(十星) 계산.
일간(日干)을 기준으로 다른 천간과의 오행·음양 관계를 10가지로 분류.
"""

from __future__ import annotations
from engine.data.heavenly_stems import STEMS_BY_KOREAN
from engine.data.wuxing import WUXING_GENERATION, WUXING_DESTRUCTION

# 지지 대표 천간 (정기 기준)
_BRANCH_TO_STEM: dict[str, str] = {
    "자": "계", "축": "기", "인": "갑", "묘": "을",
    "진": "무", "사": "병", "오": "정", "미": "기",
    "신": "경", "유": "신", "술": "무", "해": "임",
}


def calculate_ten_god(day_stem: str, target_stem: str) -> str:
    """
    일간과 대상 천간 비교 → 십성 반환.
    비견·겁재·식신·상관·편재·정재·편관·정관·편인·정인
    """
    ds = STEMS_BY_KOREAN[day_stem]
    ts = STEMS_BY_KOREAN[target_stem]
    d_el, d_yy = ds["element"], ds["yin_yang"]
    t_el, t_yy = ts["element"], ts["yin_yang"]
    same_yy = d_yy == t_yy

    if d_el == t_el:
        return "비견" if same_yy else "겁재"
    if WUXING_GENERATION.get(d_el) == t_el:
        return "식신" if same_yy else "상관"
    if WUXING_DESTRUCTION.get(d_el) == t_el:
        return "편재" if same_yy else "정재"
    if WUXING_DESTRUCTION.get(t_el) == d_el:
        return "편관" if same_yy else "정관"
    if WUXING_GENERATION.get(t_el) == d_el:
        return "편인" if same_yy else "정인"

    raise ValueError(f"십성 계산 오류: {day_stem}({d_el}) - {target_stem}({t_el})")


def generate_ten_gods_list(saju: dict) -> list[str]:
    """4기둥 천간 각각의 십성 목록 반환 [연·월·일·시]. 시주 없으면 3개."""
    day_stem = saju["day_pillar"]["stem"]
    keys = ["year_pillar", "month_pillar", "day_pillar"]
    if saju.get("hour_pillar") is not None:
        keys.append("hour_pillar")
    result = []
    for key in keys:
        stem = saju[key]["stem"]
        if stem == day_stem and key == "day_pillar":
            result.append("비견")
        else:
            result.append(calculate_ten_god(day_stem, stem))
    return result


def calculate_ten_gods_distribution(saju: dict) -> dict[str, float]:
    """
    십성 분포 계산.
    가중치: 천간 1.0 / 일반 지지 0.5 / 월지 1.5 (명리학적 月令 우위 반영)
    """
    dist: dict[str, float] = {
        g: 0.0 for g in [
            "비견", "겁재", "식신", "상관",
            "편재", "정재", "편관", "정관", "편인", "정인",
        ]
    }
    day_stem = saju["day_pillar"]["stem"]

    # 연·월·시 천간 (일간 제외) — 각 1.0
    for key in ["year_pillar", "month_pillar", "hour_pillar"]:
        if saju.get(key) is None:
            continue
        stem = saju[key]["stem"]
        dist[calculate_ten_god(day_stem, stem)] += 1.0

    # 지지 대표 천간 — 월지 1.5, 나머지 0.5
    branch_weights = {
        "year_pillar": 0.5,
        "month_pillar": 1.5,
        "day_pillar": 0.5,
        "hour_pillar": 0.5,
    }
    for key, weight in branch_weights.items():
        if saju.get(key) is None:
            continue
        branch = saju[key]["branch"]
        rep = _BRANCH_TO_STEM.get(branch)
        if rep:
            dist[calculate_ten_god(day_stem, rep)] += weight

    return dist


def get_branch_ten_god(day_stem: str, branch: str) -> str:
    """지지의 정기(대표 천간) 기준 십성 반환."""
    rep = _BRANCH_TO_STEM.get(branch)
    if rep is None:
        return ""
    return calculate_ten_god(day_stem, rep)


def get_ten_god_category(ten_god: str) -> str:
    cats = {
        "비견": "비겁", "겁재": "비겁",
        "식신": "식상", "상관": "식상",
        "편재": "재성", "정재": "재성",
        "편관": "관성", "정관": "관성",
        "편인": "인성", "정인": "인성",
    }
    return cats.get(ten_god, "")
