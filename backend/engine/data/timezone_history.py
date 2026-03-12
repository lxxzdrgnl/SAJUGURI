"""
한국 표준시 역사 테이블.
표준시 변경 및 일광절약시간(DST) 이력 기반 진태양시 보정.

참고:
  - 서울 실제 경도: 126.97° → 태양시 UTC+8:27:53 ≈ UTC+8:28
  - KST(UTC+9) 기준 보정: -(540 - 508) = -32분
  - DST 적용 시(UTC+10): -(600 - 508) = -92분
  - UTC+8:30 시기(1954-1961): -(510 - 508) = -2분
"""

from __future__ import annotations
from datetime import datetime

# ─── 표준시 변경 이력 ─────────────────────────────────────────
# (적용 시작일, UTC 오프셋 분)
_STANDARD_TIME: list[tuple[datetime, int]] = [
    (datetime(1908,  4,  1), 510),   # UTC+8:30 (대한제국)
    (datetime(1912,  1,  1), 540),   # UTC+9:00 (일본 표준시 편입)
    (datetime(1945,  9,  9), 540),   # UTC+9:00 (광복 이후 유지)
    (datetime(1954,  3, 21), 510),   # UTC+8:30 (이승만 정부 환원)
    (datetime(1961,  8, 10), 540),   # UTC+9:00 (현재, 이후 변경 없음)
]

# ─── 일광절약시간(DST) 이력 ───────────────────────────────────
# (시작일, 종료일, 추가 오프셋 분)
_DST: list[tuple[datetime, datetime, int]] = [
    (datetime(1948,  5,  1), datetime(1948,  9, 13), 60),
    (datetime(1949,  4,  3), datetime(1949,  9, 11), 60),
    (datetime(1950,  4,  1), datetime(1950,  9, 10), 60),
    (datetime(1951,  5,  6), datetime(1951,  9,  9), 60),
    (datetime(1955,  5,  5), datetime(1955,  9, 10), 60),
    (datetime(1956,  5, 20), datetime(1956,  9, 30), 60),
    (datetime(1957,  5,  5), datetime(1957,  9, 22), 60),
    (datetime(1958,  5,  4), datetime(1958,  9, 21), 60),
    (datetime(1959,  5,  3), datetime(1959,  9, 20), 60),
    (datetime(1960,  5,  1), datetime(1960,  9, 18), 60),
    # 1987·1988: 서울올림픽 전후 실시
    (datetime(1987,  5, 10), datetime(1987, 10, 12), 60),
    (datetime(1988,  5,  8), datetime(1988, 10, 10), 60),
]

# 서울 경도 기반 태양시 오프셋 (분)
_SOLAR_OFFSET_MIN: int = round(126.97 * 4)  # 508분 ≈ UTC+8:28


def get_kst_offset_minutes(dt: datetime) -> int:
    """주어진 날짜의 법적 KST UTC 오프셋 반환 (분)."""
    offset = 540  # 기본 UTC+9
    for start, off in reversed(_STANDARD_TIME):
        if dt >= start:
            offset = off
            break

    for dst_start, dst_end, add in _DST:
        if dst_start <= dt < dst_end:
            offset += add
            break

    return offset


def get_solar_correction_minutes(dt: datetime) -> int:
    """
    진태양시 보정값 반환 (분, 음수).
    KST 오프셋과 서울 실제 태양시 간의 차이.

    Examples:
        일반 KST(UTC+9):    -32분
        DST 적용(UTC+10):   -92분
        1954~1961(UTC+8:30): -2분
    """
    return _SOLAR_OFFSET_MIN - get_kst_offset_minutes(dt)


def get_solar_correction_for_location(
    dt: datetime,
    longitude: float | None = None,
    utc_offset_minutes: int | None = None,
) -> int:
    """
    출생지 경도 기반 진태양시 보정값 반환 (분).

    - longitude + utc_offset_minutes 둘 다 제공: 해외 도시 공식 적용
      correction = round(longitude × 4) − utc_offset_minutes
    - longitude만 제공 (한국 도시): 역사적 KST 테이블로 legal offset 계산
    - 둘 다 미제공: 기본 서울 보정 반환
    """
    if longitude is None:
        return get_solar_correction_minutes(dt)

    solar_offset = round(longitude * 4)

    if utc_offset_minutes is not None:
        legal_offset = utc_offset_minutes
    else:
        # 경도만 제공 → 한국 도시로 간주, 역사적 KST 사용
        legal_offset = get_kst_offset_minutes(dt)

    return solar_offset - legal_offset


def get_historical_note(dt: datetime) -> str:
    """보정 근거 메모 반환."""
    kst = get_kst_offset_minutes(dt)
    correction = get_solar_correction_minutes(dt)
    h, m = divmod(abs(kst), 60)
    is_dst = any(s <= dt < e for s, e, _ in _DST)
    note = f"UTC+{h}:{m:02d} 기준 {correction:+d}분 보정"
    if is_dst:
        note += " (일광절약시간 적용)"
    return note
