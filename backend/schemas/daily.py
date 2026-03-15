"""오늘의 운세 API 요청/응답 Pydantic 스키마."""

from __future__ import annotations
from pydantic import BaseModel, Field
from schemas.saju import SajuCalcRequest


class DailyFortuneRequest(SajuCalcRequest):
    """오늘의 운세 요청 — SajuCalcRequest + 선택적 날짜."""

    target_date: str | None = Field(
        default=None,
        description="운세 날짜 (YYYY-MM-DD). 미입력 시 오늘",
        examples=["2026-03-15"],
    )


class FortuneItem(BaseModel):
    """카테고리 하나의 운세 결과."""

    score: int  = Field(description="운세 점수 (0~100)", examples=[72])
    level: str  = Field(description="점수 구간 레벨", examples=["좋음"])
    text:  str  = Field(description="카테고리 설명 텍스트")
    label: str  = Field(description="카테고리 한글명", examples=["시험운"])


class DailyGanji(BaseModel):
    stem:   str = Field(description="오늘 천간", examples=["병"])
    branch: str = Field(description="오늘 지지", examples=["오"])


class ClothingColor(BaseModel):
    """용신/희신 오행 기반 추천 옷 색깔."""

    color:   str = Field(description="추천 색상", examples=["흰색·은색·회색"])
    element: str = Field(description="근거 오행", examples=["금"])
    reason:  str = Field(description="한 줄 이유")


class DailyFortuneResponse(BaseModel):
    """오늘의 운세 응답."""

    target_date:    str          = Field(description="운세 날짜", examples=["2026-03-15"])
    day_ganji:      DailyGanji   = Field(description="오늘 일진 간지")
    overall:        str          = Field(description="전체 요약 한 문장")
    caution:        str          = Field(description="오늘 조심해야 할 것")
    basis:          str          = Field(description="오늘 운세의 명리 근거 요약")
    clothing_color: ClothingColor = Field(description="추천 옷 색깔")
    fortunes: dict[str, FortuneItem] = Field(
        description="카테고리별 운세 (exam/money/love/career/health/social)"
    )
