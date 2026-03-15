"""
Daily Flow Engine — 오늘 간지 × 사주 상호작용.

calc_saju + 오늘 날짜 → daily_tags (오늘의 운세 RAG 쿼리 seed)

계산 항목:
  1. 세운(올해) / 월운(이번달) 간지 → 일간과의 십성 관계
  2. 현재 대운 × 세운 교차 시너지
  3. 오늘 지지 → 월지·일지와의 충·합 여부
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta, date as _date
from engine.calc.ten_gods import calculate_ten_god
from engine.calc.se_un import calc_year_ganji, calc_month_ganji, get_element_interaction

# ─── 오늘 일주 계산 (saju.py 공식 재사용) ─────────────────────────────────────

_STEMS  = ["갑","을","병","정","무","기","경","신","임","계"]
_BRANCHES = ["자","축","인","묘","진","사","오","미","신","유","술","해"]
_BASE_DATE = _date(1900, 1, 1)   # 갑술일: stemIdx=0, branchIdx=10


def _today_day_ganji(target: _date | None = None) -> dict:
    today = target or datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).date()
    delta = (today - _BASE_DATE).days
    stem   = _STEMS[delta % 10]
    branch = _BRANCHES[(delta + 10) % 12]
    return {"stem": stem, "branch": branch}


def compute_daily_flow(calc: dict, target_date: _date | None = None) -> dict:
    """
    오늘(또는 target_date)의 간지와 사주의 십성·충합 관계 계산.

    Args:
        calc        : handle_calculate_saju() 반환 dict
        target_date : 대상 날짜 (기본: 오늘)

    Returns:
        {
          "daily_tags":    ["정관일", "편재월", "역마세운", ...],
          "year_ganji":    {stem, branch, stem_element, branch_element},
          "month_ganji":   {stem, branch, ...},
          "day_ganji":     {stem, branch},
          "interactions":  [{type, label, ten_god, element_relation}, ...],
        }
    """
    today = target_date or datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).date()
    year  = today.year
    month = today.month

    day_stem = calc["day_pillar"]["stem"]
    tags: list[str] = []
    interactions: list[dict] = []

    def _make_interaction(label: str, ganji: dict) -> dict:
        ten_god = calculate_ten_god(day_stem, ganji["stem"])
        el_rel  = get_element_interaction(
            calc["day_pillar"]["stem_element"],
            ganji.get("stem_element", ""),
        )
        tags.append(f"{ten_god}_{label}")
        return {"type": label, "stem": ganji["stem"], "branch": ganji.get("branch",""),
                "ten_god": ten_god, "element_relation": el_rel}

    # 1. 세운 (올해)
    year_g = calc_year_ganji(year)
    interactions.append(_make_interaction("세운", year_g))

    # 2. 월운 (이번달)
    month_g = calc_month_ganji(year, month)
    interactions.append(_make_interaction("월운", month_g))

    # 3. 일운 (오늘)
    day_g = _today_day_ganji(today)
    ten_god_day = calculate_ten_god(day_stem, day_g["stem"])
    tags.append(f"{ten_god_day}_일운")
    interactions.append({"type": "일운", **day_g, "ten_god": ten_god_day})

    # 4. 현재 대운 십성
    cur = calc.get("current_dae_un", {})
    if cur and (tg := cur.get("stem_ten_god")):
        tags.append(f"{tg}_대운")
        tags.append("대운정점" if cur.get("start_age", 0) + 5 == datetime.now().year - int(calc["meta"]["birth_date"][:4]) else "대운진행")

    # 5. 신살 중 세운에서 활성화되는 것
    year_branch = year_g.get("branch", "")
    for sal in calc.get("sin_sals", []):
        sal_name = sal.get("name", "")
        if sal_name and year_branch:
            tags.append(f"{sal_name}_세운활성")

    return {
        "daily_tags":   list(dict.fromkeys(tags)),  # 순서 유지 중복 제거
        "year_ganji":   year_g,
        "month_ganji":  month_g,
        "day_ganji":    day_g,
        "interactions": interactions,
    }
