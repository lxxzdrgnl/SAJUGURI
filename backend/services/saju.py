"""사주 계산 서비스 — 엔진 호출 + 예외 변환."""

from __future__ import annotations
from contextlib import contextmanager
from typing import Generator

from schemas.saju import SajuCalcRequest, SajuCalcResponse
from schemas.report import SajuReportRequest, SajuReportResponse
from schemas.daily import DailyFortuneRequest, DailyFortuneResponse
from core.exceptions import (
    AppException,
    CalcFailedException,
    InvalidDateFormatException,
    LLMFailedException,
)
from engine.handlers.calculate_saju import handle_calculate_saju
from engine.handlers.get_wol_un import handle_get_wol_un
from engine.handlers.get_il_jin import handle_get_il_jin
from engine.handlers.get_yeon_un import handle_get_yeon_un
from engine.handlers.get_daily_fortune import handle_get_daily_fortune
from llm.pipelines.saju_report import run_saju_report


@contextmanager
def _calc_guard(birth_date: str | None = None) -> Generator[None, None, None]:
    """
    엔진/LLM 호출을 감싸는 예외 변환 컨텍스트 매니저.

    - AppException 계열은 그대로 통과 (이미 처리된 예외)
    - ValueError(날짜 관련) → InvalidDateFormatException (400)
    - ValueError(그 외)     → CalcFailedException (422)
    - RuntimeError          → LLMFailedException (500)  ← LLM 파싱 실패
    - Exception             → CalcFailedException (422)
    """
    try:
        yield
    except AppException:
        raise
    except ValueError as e:
        msg = str(e)
        if birth_date and ("날짜" in msg or "date" in msg.lower()):
            raise InvalidDateFormatException(birth_date)
        raise CalcFailedException(msg)
    except RuntimeError as e:
        raise LLMFailedException(str(e))
    except Exception as e:
        raise CalcFailedException(str(e))


def calc_saju(req: SajuCalcRequest) -> dict:
    with _calc_guard(req.birth_date):
        return handle_calculate_saju(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
            birth_longitude=req.birth_longitude,
            birth_utc_offset=req.birth_utc_offset,
        )


async def generate_report(req: SajuReportRequest) -> SajuReportResponse:
    with _calc_guard(req.birth_date):
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
    return SajuReportResponse(
        saju=SajuCalcResponse(**saju_dict),
        tabs=writer_output.tabs,
        concern=req.concern,
    )


def get_daily_fortune(req: DailyFortuneRequest) -> DailyFortuneResponse:
    with _calc_guard(req.birth_date):
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


def get_wol_un(year: int, day_stem: str) -> dict:
    with _calc_guard():
        return handle_get_wol_un(year=year, day_stem=day_stem)


def get_il_jin(year: int, month: int) -> dict:
    with _calc_guard():
        return handle_get_il_jin(year=year, month=month)


def get_yeon_un(start_year: int, count: int, day_stem: str) -> dict:
    with _calc_guard():
        return handle_get_yeon_un(start_year=start_year, count=count, day_stem=day_stem)
