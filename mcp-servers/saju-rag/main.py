"""
Saju-RAG MCP Server — FastMCP 진입점.
명리학 지식 베이스 RAG: 계산 없이 해석 텍스트만 반환.
"""

from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP
from tools.search import (
    handle_search_knowledge,
    handle_get_ilju_profile,
    handle_get_ten_god_profile,
    handle_get_structure_pattern,
)

mcp = FastMCP(name="saju-rag")


@mcp.tool()
def search_knowledge(
    query: str,
    categories: list[str] | None = None,
    n_results: int = 3,
) -> dict:
    """
    명리학 지식 베이스 시맨틱 검색.

    사용자의 고민이나 사주 컨텍스트를 자연어로 입력하면
    관련 명리 지식을 벡터 검색으로 반환합니다.

    Args:
        query:      검색 쿼리. 자연어로 입력 (예: "경쟁심이 강하고 독립적인 사람의 직업")
        categories: 검색 범위 ["ten_gods", "sin_sal", "gyeok_guk",
                               "structure_patterns", "wuxing", "ilju"]
                    None이면 전체 검색
        n_results:  카테고리당 반환 결과 수 (기본 3)

    Notes:
        - document: 벡터 검색에 사용된 텍스트 (semantic_context 기반)
        - metadata: 필터링 및 식별 정보
        - distance: 유사도 거리 (낮을수록 관련성 높음, cosine 기준)
    """
    return handle_search_knowledge(query, categories, n_results)


@mcp.tool()
def get_ilju_profile(ilju: str) -> dict | None:
    """
    60갑자 일주론 직접 조회.

    Args:
        ilju: 한글 일주 이름 (예: "임자", "경오", "갑자")

    Returns:
        {ilju, nickname, core, personality, career, relationship,
         strength, weakness, pillar_nuance, consulting_points, ...}
        일주 데이터가 없으면 None
    """
    return handle_get_ilju_profile(ilju)


@mcp.tool()
def get_ten_god_profile(ten_god_name: str) -> dict | None:
    """
    십성 전체 지식 직접 조회.

    Args:
        ten_god_name: 한글 십성 이름 (예: "비견", "식신", "편재", "정관")

    Returns:
        {name, personality, career, pillar_nuance, interactions,
         consulting_points, excess_warning, void_meaning, ...}
    """
    return handle_get_ten_god_profile(ten_god_name)


@mcp.tool()
def get_structure_pattern(pattern_type: str) -> dict | None:
    """
    사주 구조 패턴 해석 직접 조회.

    Args:
        pattern_type: saju-calc structure_patterns[].type 값
                      예: "sig_sang_saeng_jae", "gwan_in_sang_saeng",
                          "jae_da_sin_yak", "sang_gwan_pae_in"

    Returns:
        {name, hanja, core, strength, caution, modern, advice,
         consulting_points, ...}
    """
    return handle_get_structure_pattern(pattern_type)


@mcp.tool()
def ingest_knowledge(categories: list[str] | None = None) -> dict:
    """
    knowledge/ JSON 파일을 ChromaDB에 인덱싱.
    서버 초기화 또는 데이터 업데이트 시 호출.

    Args:
        categories: 인덱싱할 카테고리 목록. None이면 전체.

    Returns:
        {category: 삽입된 문서 수}
    """
    from lib.ingest import ingest_all, ingest_category
    if categories:
        return {cat: ingest_category(cat) for cat in categories}
    return ingest_all()


if __name__ == "__main__":
    mcp.run()
