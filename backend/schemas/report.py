"""리포트·공유 API 요청/응답 Pydantic 스키마."""

from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel, Field
from schemas.saju import SajuCalcResponse


# ─── 공통 입력 ───────────────────────────────────────────────────────────────

class BirthRequest(BaseModel):
    birth_date: str       # "YYYY-MM-DD"
    birth_time: str       # "HH:MM"
    gender: str           # "male" | "female"
    calendar: str = "solar"
    is_leap_month: bool = False


class CompatibilityRequest(BaseModel):
    person1: BirthRequest
    person2: BirthRequest


class DailyRequest(BirthRequest):
    pass


class QuestionRequest(BirthRequest):
    question: str


# ─── 사주 리포트 ─────────────────────────────────────────────────────────────

class SajuReportRequest(BaseModel):
    """사주 리포트 생성 요청."""

    birth_date: str = Field(
        description="생년월일 (YYYY-MM-DD)",
        examples=["1990-03-15"],
    )
    birth_time: str = Field(
        description="출생 시각 (HH:MM, 24시 기준). 정확한 시각 모를 경우 '12:00' 사용",
        examples=["14:30"],
    )
    gender: str = Field(
        description="성별",
        examples=["male"],
        pattern="^(male|female)$",
    )
    calendar: str = Field(
        default="solar",
        description="양력(solar) 또는 음력(lunar)",
        pattern="^(solar|lunar)$",
    )
    is_leap_month: bool = Field(default=False, description="음력 윤달 여부")
    concern: str | None = Field(
        default=None,
        description="사용자 고민 원문. 입력하면 고민 맞춤 탭이 생성됩니다.",
        examples=["이직을 고민 중인데 지금이 적기일까요?"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "birth_date": "1990-03-15",
                "birth_time": "14:30",
                "gender": "male",
                "calendar": "solar",
                "is_leap_month": False,
                "concern": "이직을 고민 중인데 지금이 적기일까요?",
            }
        }
    }


class TabContent(BaseModel):
    """리포트 탭 1개."""

    headline: str = Field(
        description="결론형 헤드라인 — 단순 카테고리명이 아닌 이 사람만을 위한 문장",
        examples=["30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자"],
    )
    content: str = Field(
        description="상세 내용 (200~400자)",
        examples=["신금(辛金) 일간은 원석을 정련한 보석과 같아..."],
    )


class WriterOutput(BaseModel):
    """Writer LLM 최종 출력 스키마."""
    tabs: list[TabContent]


class SajuReportResponse(BaseModel):
    """사주 리포트 전체 응답."""

    saju: SajuCalcResponse = Field(description="사주팔자 계산 원본 결과")
    tabs: list[TabContent] = Field(description="AI 생성 결론형 탭 목록 (10개 내외)")
    concern: str | None = Field(default=None, description="입력된 고민 원문")


# ─── 공유 링크 ────────────────────────────────────────────────────────────────

class ReportResponse(BaseModel):
    """기존 공유 링크용 응답 (호환성 유지)."""
    share_token: UUID
    feature: str
    tabs: list[TabContent]
