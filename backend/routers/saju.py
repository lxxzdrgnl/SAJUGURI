"""사주팔자 계산 API 라우터."""

from __future__ import annotations
from fastapi import APIRouter, Query
from schemas.saju import SajuCalcRequest, SajuCalcResponse
from schemas.report import SajuReportRequest, SajuReportResponse
from schemas.daily import DailyFortuneRequest, DailyFortuneResponse
from core.errors import SWAGGER_ERRORS
from core.exceptions import CalcFailedException, InvalidDateFormatException
from engine.handlers.calculate_saju import handle_calculate_saju
from engine.handlers.get_wol_un import handle_get_wol_un
from engine.handlers.get_il_jin import handle_get_il_jin
from engine.handlers.get_yeon_un import handle_get_yeon_un
from engine.handlers.get_daily_fortune import handle_get_daily_fortune
from llm.pipelines.saju_report import run_saju_report

router = APIRouter(prefix="/api/saju", tags=["사주 계산"])


@router.post(
    "/calc",
    response_model=SajuCalcResponse,
    summary="사주팔자 계산",
    description="""
생년월일시와 성별을 입력하면 사주팔자 전체를 계산합니다.

**계산 내용**:
- 4기둥 (연·월·일·시주) — 천간·지지·십성·12운성
- 오행·음양 분포 비율
- 일간 강약 (very_strong / strong / medium / weak / very_weak)
- 격국 (편재격·칠살격·정관격·식신격 등 13종)
- 용신·희신·기신 선정 (억부/조후/통관)
- 신살 (역마살·도화살·귀문관살·양인살 등, RAG 우선순위 포함)
- 지장간·지지 관계 (충·합·형·해·파)
- 대운 10구간 + 현재 대운
- 구조 패턴·동역학·시너지 (Writer Agent용)
- 행동 프로파일·생활 도메인 (RAG 쿼리 seed)

**시각 보정**:
동경 127° 기준으로 표준시를 보정합니다 (통상 -30~-32분).
역사적 표준시 변경(일제강점기·해방 후)도 자동 적용됩니다.

**음력 입력**:
`calendar: "lunar"` 설정 시 음력 날짜로 처리합니다.
윤달은 `is_leap_month: true`로 구분합니다.
""",
    responses={
        200: {
            "description": "사주팔자 계산 성공",
            "content": {
                "application/json": {
                    "example": SajuCalcResponse.model_config["json_schema_extra"]["example"]
                }
            },
        },
        **{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)},
    },
)
async def calculate_saju(req: SajuCalcRequest) -> SajuCalcResponse:
    try:
        result = handle_calculate_saju(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
        )
        return result
    except ValueError as e:
        msg = str(e)
        if "날짜" in msg or "date" in msg.lower():
            raise InvalidDateFormatException(req.birth_date)
        raise CalcFailedException(msg)
    except Exception as e:
        raise CalcFailedException(str(e))


@router.post(
    "/report",
    response_model=SajuReportResponse,
    summary="AI 사주 리포트 생성",
    description="""
사주팔자 계산 + RAG 지식 검색 + Writer LLM을 한 번에 실행하여
결론형 헤드라인 탭 리포트를 반환합니다.

**처리 순서**:
1. 사주팔자 12단계 계산 (Engine)
2. ChromaDB + 지식 JSON 기반 RAG 컨텍스트 조립 (deterministic)
3. Writer LLM → 10개 결론형 탭 생성

**고민 입력 시**: 고민 맞춤 탭이 우선 생성됩니다.
""",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def generate_saju_report(req: SajuReportRequest) -> SajuReportResponse:
    try:
        saju_dict, writer_output = await run_saju_report(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            concern=req.concern,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
        )
        saju_response = SajuCalcResponse(**saju_dict)
        return SajuReportResponse(
            saju=saju_response,
            tabs=writer_output.tabs,
            concern=req.concern,
        )
    except ValueError as e:
        msg = str(e)
        if "날짜" in msg or "date" in msg.lower():
            raise InvalidDateFormatException(req.birth_date)
        raise CalcFailedException(msg)
    except RuntimeError as e:
        raise CalcFailedException(str(e))
    except Exception as e:
        raise CalcFailedException(str(e))


@router.post(
    "/daily",
    response_model=DailyFortuneResponse,
    summary="오늘의 운세",
    description="""
생년월일시와 성별을 입력하면 오늘의 운세를 6개 카테고리로 반환합니다.

**카테고리**: 시험운 · 재물운 · 연애운 · 직장운 · 건강운 · 대인관계운

**계산 방식**:
- 오늘 간지 × 일간 십성 → 카테고리별 점수
- 오늘 지지 오행 × 용신/희신/기신 → 오행 보정
- 오늘 지지 vs 일지·월지 충합 관계 → 관계 보정
- 랜덤 없음: 동일 입력은 항상 동일 결과 반환

**target_date**: 미입력 시 오늘 날짜 기준으로 계산합니다.
""",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def get_daily_fortune(req: DailyFortuneRequest) -> DailyFortuneResponse:
    try:
        result = handle_get_daily_fortune(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
            target_date=req.target_date,
        )
        return DailyFortuneResponse(**result)
    except ValueError as e:
        msg = str(e)
        if "날짜" in msg or "date" in msg.lower():
            raise InvalidDateFormatException(req.birth_date)
        raise CalcFailedException(msg)
    except Exception as e:
        raise CalcFailedException(str(e))


@router.get(
    "/wol-un",
    summary="월운 조회",
    description="특정 연도의 월운 간지 12개를 반환합니다. `day_stem`은 사주 계산 결과의 일간 천간입니다.",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def get_wol_un(
    year:      int = Query(..., ge=1900, le=2100, description="대상 연도"),
    day_stem:  str = Query(..., description="일간 천간 (갑/을/병/정/무/기/경/신/임/계)"),
):
    try:
        return handle_get_wol_un(year=year, day_stem=day_stem)
    except ValueError as e:
        raise CalcFailedException(str(e))
    except Exception as e:
        raise CalcFailedException(str(e))


@router.get(
    "/il-jin",
    summary="일진 달력 조회",
    description="특정 년·월의 일별 일진(간지)과 음력 날짜를 반환합니다.",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def get_il_jin(
    year:  int = Query(..., ge=1900, le=2100, description="연도"),
    month: int = Query(..., ge=1,    le=12,   description="월"),
):
    try:
        return handle_get_il_jin(year=year, month=month)
    except ValueError as e:
        raise CalcFailedException(str(e))
    except Exception as e:
        raise CalcFailedException(str(e))


@router.get(
    "/yeon-un",
    summary="연운(세운) 조회",
    description="특정 구간의 연운 간지 목록을 반환합니다. `day_stem`은 사주 일간 천간입니다.",
    responses={**{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)}},
)
async def get_yeon_un(
    start_year: int = Query(..., ge=1900, le=2100, description="시작 연도"),
    count:      int = Query(10,  ge=1,    le=20,   description="반환할 연도 수 (최대 20)"),
    day_stem:   str = Query(..., description="일간 천간 (갑/을/병/정/무/기/경/신/임/계)"),
):
    try:
        return handle_get_yeon_un(start_year=start_year, count=count, day_stem=day_stem)
    except ValueError as e:
        raise CalcFailedException(str(e))
    except Exception as e:
        raise CalcFailedException(str(e))
