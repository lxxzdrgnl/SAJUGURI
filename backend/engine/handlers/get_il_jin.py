"""일진(日辰) 달력 핸들러."""

from __future__ import annotations
from engine.calc.il_jin import get_il_jin_calendar
from engine.calc.validation import validate_year_month


def handle_get_il_jin(year: int, month: int) -> list:
    """
    특정 년·월의 일진 달력 반환.

    Returns:
        IlJinEntry 리스트 (date, stem, branch, ganji_name, lunar_month, lunar_day, is_leap_month, solar_term)
    """
    validate_year_month(year, month)
    raw = get_il_jin_calendar(year, month)
    result = []
    for day in raw["days"]:
        ganji = day["ganji"]
        result.append({
            "date":         day["date"],
            "stem":         ganji["stem"],
            "branch":       ganji["branch"],
            "ganji_name":   ganji["ganji_name"],
            "lunar_month":  day["lunar_month"],
            "lunar_day":    day["lunar_day"],
            "is_leap_month": day["is_leap"],
            "solar_term":   day["solar_term"],
        })
    return result
