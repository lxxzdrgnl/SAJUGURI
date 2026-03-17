"""한줄 상담 요청/응답 Pydantic 스키마."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


CATEGORIES = Literal['career', 'love', 'money', 'health', 'general']


class QuestionRequest(BaseModel):
    """한줄 상담 요청."""

    birth_date: str = Field(description="생년월일 (YYYY-MM-DD)", examples=["1990-03-15"])
    birth_time: str | None = Field(default=None, description="출생 시각 (HH:MM). 모를 경우 null", examples=["14:30"])
    gender: str = Field(description="성별", examples=["male"], pattern="^(male|female)$")
    calendar: str = Field(default="solar", pattern="^(solar|lunar)$")
    is_leap_month: bool = Field(default=False)
    birth_longitude: float | None = Field(default=None)
    birth_utc_offset: int | None = Field(default=None)

    question: str = Field(
        description="고민 원문 (10~200자)",
        min_length=10,
        max_length=100,
        examples=["올해 이직 운이 있을까요?"],
    )
    category: CATEGORIES | None = Field(
        default=None,
        description="고민 카테고리. 생략 시 LLM이 자동 분류",
        examples=["career"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "birth_date": "1990-03-15",
                "birth_time": "14:30",
                "gender": "male",
                "calendar": "solar",
                "is_leap_month": False,
                "question": "올해 이직 운이 있을까요?",
                "category": "career",
            }
        }
    }


class ConsultationOutput(BaseModel):
    """한줄 상담 Writer 출력."""
    headline: str = Field(
        description="결론형 한 문장 (30자 내외)",
        examples=["변화의 파도가 이미 당신 발아래까지 왔습니다"],
    )
    content: str = Field(
        description="상세 내용 (300~500자)",
        examples=["정관격에 식상운이 들어온 지금..."],
    )


class QuestionResponse(BaseModel):
    """한줄 상담 API 응답 (자동 저장, id 포함)."""
    id:       int
    headline: str
    content:  str
    category: str


class ConsultationHistoryItem(BaseModel):
    """상담 기록 목록 아이템."""
    id:          int
    question:    str
    category:    str
    headline:    str
    content:     str
    created_at:  datetime
    share_token: str | None = None

    model_config = {"from_attributes": True}


class ConsultationDetail(BaseModel):
    """상담 상세 (공유 링크용 포함)."""
    id:          int
    question:    str
    category:    str
    headline:    str
    content:     str
    created_at:  datetime
    share_token: str | None = None

    model_config = {"from_attributes": True}


class ShareTokenResponse(BaseModel):
    """공유 토큰 응답."""
    share_token: str
