"""
입력 검증 유틸리티.
"""

from __future__ import annotations
import re
from datetime import date


class ValidationError(ValueError):
    pass


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def validate_birth_input(
    birth_date: str,
    birth_time: str | None,
    gender: str,
    calendar: str = "solar",
) -> None:
    """
    사주 입력값 검증. 유효하지 않으면 ValidationError 발생.
    """
    # 날짜 형식
    if not _DATE_RE.match(birth_date):
        raise ValidationError(f"날짜 형식 오류 (YYYY-MM-DD): {birth_date}")

    y, m, d = map(int, birth_date.split("-"))
    if not (1900 <= y <= 2100):
        raise ValidationError(f"연도 범위 초과 (1900-2100): {y}")
    try:
        date(y, m, d)
    except ValueError as e:
        raise ValidationError(f"유효하지 않은 날짜: {birth_date}") from e

    # 시간 형식 (None이면 시주 미산출로 처리 — 스킵)
    if birth_time is not None:
        if not _TIME_RE.match(birth_time):
            raise ValidationError(f"시간 형식 오류 (HH:MM): {birth_time}")
        hh, mm = map(int, birth_time.split(":"))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValidationError(f"유효하지 않은 시간: {birth_time}")

    # 성별
    if gender not in ("male", "female"):
        raise ValidationError(f"성별은 'male' 또는 'female': {gender}")

    # 달력 종류
    if calendar not in ("solar", "lunar"):
        raise ValidationError(f"달력은 'solar' 또는 'lunar': {calendar}")


def validate_year_month(year: int, month: int) -> None:
    if not (1900 <= year <= 2100):
        raise ValidationError(f"연도 범위 초과 (1900-2100): {year}")
    if not (1 <= month <= 12):
        raise ValidationError(f"월 범위 오류 (1-12): {month}")
