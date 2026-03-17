"""
RAG 검색 tool 핸들러.

Tool 분류:
  - search_knowledge        : 범용 자연어 시맨틱 검색
  - search_by_context       : calc 출력(context_ranking, life_domains) → Writer용 RAG 결과 조립
  - get_ilju_profile        : 일주 직접 조회 (벡터 검색 불필요)
  - get_ten_god_profile     : 십성 직접 조회
  - get_structure_pattern   : 구조 패턴 직접 조회
  - get_sin_sal_profile     : 신살 직접 조회
"""

from __future__ import annotations
import json
import functools
from pathlib import Path
from rag.db import search, search_multi, COLLECTIONS

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


# ─── 직접 조회 헬퍼 ────────────────────────────────────────────────────

@functools.lru_cache(maxsize=16)
def _load_knowledge(category: str) -> tuple[dict, ...]:
    """JSON 파일 파싱 결과를 메모리에 캐싱 (프로세스 수명 동안 유지)."""
    filepath = _KNOWLEDGE_DIR / f"{category}.json"
    if not filepath.exists():
        return ()
    with open(filepath, encoding="utf-8") as f:
        return tuple(json.load(f))


def _find_by_field(category: str, field: str, value: str) -> dict | None:
    for entry in _load_knowledge(category):  # tuple[dict, ...]
        if entry.get(field) == value:
            return entry
    return None


# ─── 범용 시맨틱 검색 ───────────────────────────────────────────────────

def handle_search_knowledge(
    query: str,
    categories: list[str] | None = None,
    n_results: int = 3,
    where: dict | None = None,
) -> dict:
    """
    지식 베이스 시맨틱 검색.

    Returns:
        {category: [{id, document, metadata, distance}]}
    """
    if categories and len(categories) == 1 and where is None:
        results = search(categories[0], query, n_results)
        return {categories[0]: results}
    return search_multi(query, categories, n_results)


# ─── calc 출력 → Writer용 RAG 결과 조립 ────────────────────────────────

def handle_search_by_context(
    context_ranking: dict,
    life_domains: dict,
    day_pillar: str | None = None,
    concern: str | None = None,
    # 추가 calc 필드
    branch_relations: dict | None = None,
    dynamics: dict | None = None,
    day_master_strength: dict | None = None,
    yong_sin: dict | None = None,
    sin_sals: list[dict] | None = None,
    n_per_domain: int = 2,
) -> dict:
    """
    saju-calc 출력 전체 → Writer용 RAG 청크 조립.

    Args:
        context_ranking      : {"primary_context": [...], "secondary_context": [...]}
        life_domains         : {"career": [...], "relationship": [...], ...}
        day_pillar           : 일주 간지 (예: "경오")
        concern              : 사용자 고민 원문
        branch_relations     : 충·합·형·해·파 관계 dict
        dynamics             : 천간합·통근·충합 위치 정보
        day_master_strength  : {"level_8": "중화신강", "score": 62, ...}
        yong_sin             : {"primary": "금", "logic_type": "억부", ...}
        sin_sals             : 활성 신살 목록 [{name, type, priority, location}, ...]
        n_per_domain         : 도메인별 시맨틱 검색 결과 수

    Returns:
        {
          "career":        [RAG chunk, ...],
          "relationship":  [RAG chunk, ...],
          "wealth":        [RAG chunk, ...],
          "personality":   [RAG chunk, ...],
          "context":       [RAG chunk, ...],   # primary_context 직접 조회
          "ilju":          {일주 전체 지식} or None,
          "concern":       [RAG chunk, ...],
          "dynamics":      [RAG chunk, ...],   # 합충 관계 기반 검색
          "sin_sal_all":   [{name, priority, location, data}, ...],  # 전체 신살 지식
          "strength":      str | None,         # 신강/신약 레이블 (Writer 참고용)
          "yong_sin_summary": str | None,      # 용신 요약 (Writer 참고용)
        }
    """
    result: dict = {
        "career": [], "relationship": [], "wealth": [], "personality": [],
        "context": [], "ilju": None, "concern": [],
        "concern_hints": [],  # interpretation_tags 기반 규칙형 힌트
        "dynamics": [], "sin_sal_all": [], "strength": None, "yong_sin_summary": None,
    }

    # 1. life_domain별 시맨틱 검색 (ten_gods + structure_patterns + wuxing)
    domain_collections = ["ten_gods", "structure_patterns", "wuxing"]
    for domain, tags in life_domains.items():
        if domain not in result:
            continue
        # tags가 비어있으면 도메인명을 fallback 쿼리로 사용
        query = " ".join(tags) if tags else domain
        chunks = []
        for col in domain_collections:
            hits = search(col, query, n_per_domain)
            chunks.extend(hits)
        chunks.sort(key=lambda x: x.get("distance") or 1.0)
        result[domain] = chunks[: n_per_domain * 2]

    # 2. primary_context / secondary_context 직접 조회
    all_ctx = (
        context_ranking.get("primary_context", []) +
        context_ranking.get("secondary_context", [])
    )
    for ctx in all_ctx:
        ctx_id   = ctx.get("id", "")
        ctx_type = ctx.get("type", "")
        if ctx_type == "pattern":
            entry = handle_get_structure_pattern(ctx_id)
        elif ctx_type == "sin_sal":
            entry = _find_by_field("sin_sal", "name", ctx_id)
        else:
            entry = None
        if entry:
            result["context"].append({"id": ctx_id, "type": ctx_type, "data": entry})

    # 3. 일주 직접 조회
    if day_pillar:
        result["ilju"] = _find_by_field("ilju", "ilju", day_pillar)

    # 4. concern 시맨틱 검색 + interpretation_tags 기반 힌트 추출
    if concern:
        concern_chunks = search_multi(concern, ["ten_gods", "sin_sal", "structure_patterns"], 2)
        for hits in concern_chunks.values():
            result["concern"].extend(hits)
        result["concern"].sort(key=lambda x: x.get("distance") or 1.0)
        result["concern"] = result["concern"][:4]

        # interpretation_tags → 규칙형 힌트 (문장 아닌 태그 키워드)
        seen: set[str] = set()
        for hit in result["concern"]:
            tags_str = hit.get("metadata", {}).get("interpretation_tags", "")
            for tag in tags_str.split(","):
                tag = tag.strip()
                if tag and tag not in seen:
                    seen.add(tag)
                    result["concern_hints"].append(tag)
        result["concern_hints"] = result["concern_hints"][:12]

    # 5. 충·합·형·해·파 기반 dynamics 검색
    if branch_relations or dynamics:
        _dyn_keywords: list[str] = []

        br = branch_relations or {}
        # 합화 관계 → 합화 오행 키워드
        for hap in br.get("yuk_hap", []):
            if hap.get("is_effective") and hap.get("element"):
                _dyn_keywords.append(f"육합 {hap['element']}화")
        if br.get("sam_hap"):
            sh = br["sam_hap"]
            _dyn_keywords.append(f"삼합 {sh.get('element', '')}화")
        if br.get("cheon_gan_hap"):
            for h in br["cheon_gan_hap"]:
                _dyn_keywords.append(f"천간합 {h.get('name', '')}")
        # 충
        for pair in br.get("chung", []):
            _dyn_keywords.append(f"{''.join(pair)}충")
        # 형
        for name in br.get("sam_hyeong", []):
            _dyn_keywords.append(f"{name}")

        # dynamics 천간합·통근 추가
        if dynamics:
            for sh in dynamics.get("stem_hap", []):
                _dyn_keywords.append(sh.get("name", ""))
            if dynamics.get("rooting_map"):
                _dyn_keywords.append("통근 통기")

        if _dyn_keywords:
            dyn_query = " ".join(filter(None, _dyn_keywords))
            dyn_hits = search_multi(dyn_query, ["dynamics", "structure_patterns"], n_per_domain)
            for hits in dyn_hits.values():
                result["dynamics"].extend(hits)
            result["dynamics"].sort(key=lambda x: x.get("distance") or 1.0)
            result["dynamics"] = result["dynamics"][:4]

    # 6. 신강/신약 레이블 → Writer 직접 참고용 (RAG 검색 아님, 메타데이터)
    if day_master_strength:
        result["strength"] = day_master_strength.get("level_8")

    # 7. 용신 요약 → Writer 직접 참고용
    if yong_sin:
        primary = yong_sin.get("primary", "")
        logic   = yong_sin.get("logic_type", "")
        xi_sin  = "·".join(yong_sin.get("xi_sin", []))
        result["yong_sin_summary"] = f"용신:{primary} ({logic}), 희신:{xi_sin}"

    # 8. 전체 활성 신살 상세 지식 조회 (우선순위 무관, pillar_nuance 포함)
    if sin_sals:
        for ss in sin_sals:
            name = ss.get("name", "")
            if not name:
                continue
            entry = _find_by_field("sin_sal", "name", name)
            if entry:
                result["sin_sal_all"].append({
                    "name": name,
                    "priority": ss.get("priority", "low"),
                    "location": ss.get("location", []),
                    "data": entry,
                })

    return result


# ─── 직접 조회 핸들러 ───────────────────────────────────────────────────

def handle_get_ilju_profile(ilju: str) -> dict | None:
    """일주(예: '경오') 전체 지식 직접 조회."""
    return _find_by_field("ilju", "ilju", ilju)


def handle_get_ten_god_profile(ten_god_name: str) -> dict | None:
    """십성 이름으로 전체 지식 직접 조회."""
    return _find_by_field("ten_gods", "name", ten_god_name)


def handle_get_structure_pattern(pattern_id: str) -> dict | None:
    """
    구조 패턴 id로 전체 지식 직접 조회.

    calc 출력(예: 'sig_sang_saeng_jae')과 RAG 파일 id(예: 'sp_sig_sang_saeng_jae') 모두 처리.
    """
    # calc는 prefix 없이 반환하므로 'sp_' 자동 보완
    result = _find_by_field("structure_patterns", "id", pattern_id)
    if result is None:
        result = _find_by_field("structure_patterns", "id", f"sp_{pattern_id}")
    return result


def handle_get_sin_sal_profile(sin_sal_name: str) -> dict | None:
    """신살 이름으로 전체 지식 직접 조회 (예: '역마살', '귀문관살')."""
    return _find_by_field("sin_sal", "name", sin_sal_name)
