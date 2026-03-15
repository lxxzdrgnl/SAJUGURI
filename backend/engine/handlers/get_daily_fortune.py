"""오늘의 운세 핸들러."""

from __future__ import annotations
from datetime import date as _date

from engine.handlers.calculate_saju import handle_calculate_saju
from engine.calc.daily_fortune import compute_daily_fortune


def handle_get_daily_fortune(
    birth_date: str,
    birth_time: str | None,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
    birth_longitude: float | None = None,
    birth_utc_offset: int | None = None,
    target_date: str | None = None,
) -> dict:
    """
    사주 계산 → 오늘의 운세 반환.

    Returns:
        compute_daily_fortune() 결과 dict
    """
    calc = handle_calculate_saju(
        birth_date=birth_date,
        birth_time=birth_time,
        gender=gender,
        calendar=calendar,
        is_leap_month=is_leap_month,
        birth_longitude=birth_longitude,
        birth_utc_offset=birth_utc_offset,
    )

    td: _date | None = None
    if target_date:
        td = _date.fromisoformat(target_date)

    return compute_daily_fortune(calc, td)
