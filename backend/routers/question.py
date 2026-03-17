"""한줄 상담 API 라우터."""

from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Consultation, User
from dependencies.auth import get_current_user, get_optional_user
from dependencies.db import get_db
from schemas.question import (
    QuestionRequest,
    QuestionResponse,
    ConsultationHistoryItem,
    ConsultationDetail,
    ShareTokenResponse,
)
from core.errors import SWAGGER_ERRORS
from core.exceptions import CalcFailedException
from llm.pipelines.question import run_question_consultation

router = APIRouter(prefix="/api/question", tags=["한줄 상담"])


@router.post(
    "",
    response_model=QuestionResponse,
    summary="한줄 상담",
    description="""
생년월일시 + 고민(10~100자)을 입력하면 사주 기반 AI 단답형 상담을 반환합니다.
결과는 자동으로 DB에 저장됩니다. 로그인 시 사용자 계정과 연결됩니다.

**처리 흐름**:
1. 사주 계산 (Engine)
2. 고민 + 카테고리 + 사주 키워드 기반 RAG 검색
3. 용신/기신 기반 Reranking (일반론 억제)
4. Chain-of-Thought Writer (headline + content)
5. DB 자동 저장

**카테고리**: career(직업) / love(연애) / money(재물) / health(건강) / general(일반)
""",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def ask_question(
    req: QuestionRequest,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> QuestionResponse:
    try:
        result = await run_question_consultation(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
            question=req.question,
        )
    except Exception as exc:
        raise CalcFailedException(str(exc)) from exc

    # 자동 저장 (로그인 시 user_id 연결, 비로그인은 null)
    birth_input = {
        "birth_date": req.birth_date,
        "birth_time": req.birth_time,
        "gender": req.gender,
        "calendar": req.calendar,
        "is_leap_month": req.is_leap_month,
        "birth_longitude": req.birth_longitude,
        "birth_utc_offset": req.birth_utc_offset,
    }
    row = Consultation(
        user_id=user.id if user else None,
        birth_input=birth_input,
        question=req.question,
        category=result.get("category", "general"),
        headline=result["headline"],
        content=result["content"],
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return QuestionResponse(
        id=row.id,
        headline=row.headline,
        content=row.content,
        category=row.category,
    )


@router.get(
    "/history",
    response_model=list[ConsultationHistoryItem],
    summary="내 상담 기록",
)
async def list_consultations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConsultationHistoryItem]:
    result = await db.execute(
        select(Consultation)
        .where(Consultation.user_id == user.id)
        .order_by(Consultation.created_at.desc())
        .limit(50)
    )
    rows = result.scalars().all()
    return [
        ConsultationHistoryItem(
            id=r.id,
            question=r.question,
            category=r.category,
            headline=r.headline,
            content=r.content,
            created_at=r.created_at,
            share_token=str(r.share_token) if r.share_token else None,
        )
        for r in rows
    ]


@router.post(
    "/{consultation_id}/share",
    response_model=ShareTokenResponse,
    summary="공유 링크 생성",
)
async def create_share(
    consultation_id: int,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> ShareTokenResponse:
    result = await db.execute(
        select(Consultation).where(Consultation.id == consultation_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="상담 기록을 찾을 수 없습니다.")
    # 로그인 상담은 본인만 공유 가능
    if row.user_id is not None and (user is None or user.id != row.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
    if not row.share_token:
        row.share_token = uuid.uuid4()
        await db.commit()
        await db.refresh(row)
    return ShareTokenResponse(share_token=str(row.share_token))


@router.delete(
    "/{consultation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="상담 기록 삭제",
)
async def delete_consultation(
    consultation_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.user_id == user.id,
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="상담 기록을 찾을 수 없습니다.")
    await db.delete(row)
    await db.commit()


@router.get(
    "/share/{token}",
    response_model=ConsultationDetail,
    summary="공유된 상담 조회 (비로그인 가능)",
)
async def get_shared_consultation(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> ConsultationDetail:
    try:
        token_uuid = uuid.UUID(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 공유 링크입니다.")
    result = await db.execute(
        select(Consultation).where(Consultation.share_token == token_uuid)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="상담 기록을 찾을 수 없습니다.")
    name = None
    if row.birth_input and isinstance(row.birth_input, dict):
        name = row.birth_input.get("name") or None
    return ConsultationDetail(
        id=row.id,
        name=name,
        question=row.question,
        category=row.category,
        headline=row.headline,
        content=row.content,
        created_at=row.created_at,
        share_token=str(row.share_token),
    )
