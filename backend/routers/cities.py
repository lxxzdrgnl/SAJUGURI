"""도시 검색 API — 한국어/영문 통합 검색, 좌표·타임존 반환."""

from __future__ import annotations
import functools
import re
import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/cities", tags=["도시 검색"])


class CityResult(BaseModel):
    label: str       # 표시명 (검색어 언어 우선)
    sublabel: str    # 국가명
    longitude: float
    utc_offset: int  # 분 단위 표준시 (1월 기준, 비DST)
    timezone: str
    is_korea: bool


@functools.lru_cache(maxsize=1)
def _load_gc():
    import geonamescache
    return geonamescache.GeonamesCache()


@functools.lru_cache(maxsize=1)
def _load_tf():
    from timezonefinder import TimezoneFinder
    return TimezoneFinder()


def _utc_offset_minutes(tz: str) -> int:
    """IANA 타임존 → 표준시 UTC 오프셋(분). 1월 기준(비DST)."""
    try:
        ref = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo(tz))
        return int(ref.utcoffset().total_seconds() / 60)
    except (ZoneInfoNotFoundError, Exception):
        return 0


_IS_KOREAN = re.compile(r"[가-힣]")


@router.get("", response_model=list[CityResult])
def search_cities(q: str = Query(..., min_length=1, max_length=100)):
    """
    한국어 또는 영문으로 도시 검색.
    - 한글 입력 → GeoNames alternateNames에서 ko 매칭
    - 영문 입력 → GeoNames name/asciiname prefix 매칭
    최대 8개 반환.
    """
    gc = _load_gc()
    tf = _load_tf()
    q = q.strip()
    is_korean = bool(_IS_KOREAN.search(q))
    results: list[CityResult] = []

    cities: dict = gc.get_cities()

    for city in cities.values():
        if len(results) >= 8:
            break

        name: str = city.get("name", "")
        ascii_name: str = city.get("asciiname", "")
        alt_names: list[str] = city.get("alternatenames", [])
        lat: float = city.get("latitude", 0)
        lng: float = city.get("longitude", 0)
        country_code: str = city.get("countrycode", "")

        if is_korean:
            # 한국어 alternate names에서 매칭
            ko_matches = [n for n in alt_names if _IS_KOREAN.search(n) and q in n]
            if not ko_matches:
                continue
            label = ko_matches[0]
        else:
            q_lower = q.lower()
            if not (name.lower().startswith(q_lower) or ascii_name.lower().startswith(q_lower)):
                continue
            label = name

        # 타임존 조회
        tz = tf.timezone_at(lat=lat, lng=lng) or ""
        if not tz:
            continue

        utc_off = _utc_offset_minutes(tz)
        country_name = gc.get_countries().get(country_code, {}).get("name", country_code)

        results.append(CityResult(
            label=label,
            sublabel=f"{name}, {country_name}" if is_korean else country_name,
            longitude=lng,
            utc_offset=utc_off,
            timezone=tz,
            is_korea=country_code == "KR",
        ))

    return results
