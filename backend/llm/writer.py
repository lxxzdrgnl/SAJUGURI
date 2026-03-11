"""
Writer LLM — PydanticOutputParser 기반 사주 리포트 생성기.

입력: 사주 계산 결과 + RAG 컨텍스트 + 사용자 고민
출력: WriterOutput (10개 결론형 탭)
"""

from __future__ import annotations
import logging
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.messages import SystemMessage, HumanMessage

from schemas.report import WriterOutput
from llm.providers import get_llm
from llm.prompts import SYSTEM_PROMPT, format_user_message

logger = logging.getLogger(__name__)


async def generate_report(
    saju: dict,
    rag_ctx: dict,
    concern: str | None = None,
    provider: str | None = None,
) -> WriterOutput:
    """
    사주 데이터 + RAG 컨텍스트를 받아 WriterOutput을 생성한다.

    Args:
        saju     : handle_calculate_saju() 반환 dict
        rag_ctx  : build_rag_context() 반환 dict
        concern  : 사용자 고민 원문
        provider : LLM provider 오버라이드 (None → settings 기본값)

    Returns:
        WriterOutput (tabs: list[TabContent])
    """
    llm = get_llm(provider)

    # ── 1. PydanticOutputParser 생성 ──
    parser: PydanticOutputParser[WriterOutput] = PydanticOutputParser(
        pydantic_object=WriterOutput
    )
    format_instructions = parser.get_format_instructions()

    # ── 2. 메시지 조립 ──
    user_text = format_user_message(saju, rag_ctx, concern, format_instructions)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_text),
    ]

    # ── 3. LLM 호출 ──
    try:
        response = await llm.ainvoke(messages)
        raw = response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        logger.error("Writer LLM 호출 실패: %s", exc)
        raise

    # ── 4. 파싱 (실패 시 OutputFixingParser로 재시도) ──
    try:
        return parser.parse(raw)
    except Exception as parse_exc:
        logger.warning("1차 파싱 실패, OutputFixingParser 재시도: %s", parse_exc)
        try:
            fixing_parser = OutputFixingParser.from_llm(
                parser=parser,
                llm=get_llm(provider),
            )
            return fixing_parser.parse(raw)
        except Exception as fix_exc:
            logger.error("OutputFixingParser도 실패: %s", fix_exc)
            raise RuntimeError(f"Writer 출력 파싱 최종 실패: {fix_exc}") from fix_exc
