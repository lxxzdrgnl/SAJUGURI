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


@functools.lru_cache(maxsize=64)
def _build_index(category: str, field: str) -> dict[str, dict]:
    """카테고리+필드 기준 O(1) 조회 인덱스."""
    return {e[field]: e for e in _load_knowledge(category) if field in e}


def _find_by_field(category: str, field: str, value: str) -> dict | None:
    return _build_index(category, field).get(value)


# ─── 태그 기반 규칙 매칭 (시맨틱 검색 대체) ─────────────────────────────

def _collect_entry_tags(entry: dict) -> set[str]:
    """지식 항목에서 매칭 가능한 모든 태그 수집."""
    tags: set[str] = set()
    for field in ("engine_tags", "interpretation_tags", "behavior_vector",
                   "personality_vector", "career_hint"):
        if vals := entry.get(field):
            tags.update(vals)
    if lp := entry.get("life_patterns"):
        for domain_tags in lp.values():
            tags.update(domain_tags)
    if ch := entry.get("career_hint"):
        tags.update(ch)
    return tags


def _match_by_tags(
    query_tags: list[str],
    categories: list[str],
    top_n: int = 4,
) -> list[dict]:
    """
    Engine life_domain 태그 → 지식 항목의 태그와 직접 매칭.

    시맨틱 검색 대신 사용. 영어↔영어 태그 비교이므로 언어 불일치 없음.
    임베딩 API 호출 0회.
    """
    if not query_tags:
        return []

    query_set = set(query_tags)
    scored: list[tuple[int, str, dict]] = []

    for cat in categories:
        for entry in _load_knowledge(cat):
            entry_tags = _collect_entry_tags(entry)
            overlap = len(query_set & entry_tags)
            if overlap > 0:
                scored.append((overlap, cat, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "id": entry.get("id", ""),
            "category": cat,
            "score": score,
            "data": entry,
        }
        for score, cat, entry in scored[:top_n]
    ]


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
    n_per_domain: int = 4,
) -> dict:
    """
    saju-calc 출력 전체 → Writer용 RAG 청크 조립.

    변경사항 (v2):
      - 도메인별 검색: 시맨틱 → 태그 매칭 (언어 불일치 해결, 임베딩 0회)
      - concern만 시맨틱 검색 유지 (사용자 자연어 입력)
      - dynamics: 키워드 직접 조회로 전환
      - 신살 중복 제거
    """
    result: dict = {
        "career": [], "relationship": [], "wealth": [], "personality": [],
        "context": [], "ilju": None, "concern": [],
        "concern_hints": [],
        "dynamics": [], "sin_sal_all": [], "strength": None, "yong_sin_summary": None,
    }

    # 1. life_domain별 태그 매칭 (임베딩 호출 0회)
    domain_collections = ["ten_gods", "structure_patterns", "wuxing"]
    for domain, tags in life_domains.items():
        if domain not in result:
            continue
        matched = _match_by_tags(tags if tags else [], domain_collections, n_per_domain)
        result[domain] = matched

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

    # 4. concern 시맨틱 검색 (사용자 자연어 → 벡터 검색이 유효한 유일한 지점)
    if concern:
        concern_chunks = search_multi(concern, ["ten_gods", "sin_sal", "structure_patterns"], 2)
        for hits in concern_chunks.values():
            result["concern"].extend(hits)
        result["concern"].sort(key=lambda x: x.get("distance") or 1.0)
        result["concern"] = result["concern"][:4]

        # interpretation_tags → 규칙형 힌트
        seen: set[str] = set()
        for hit in result["concern"]:
            tags_str = hit.get("metadata", {}).get("interpretation_tags", "")
            for tag in tags_str.split(","):
                tag = tag.strip()
                if tag and tag not in seen:
                    seen.add(tag)
                    result["concern_hints"].append(tag)
        result["concern_hints"] = result["concern_hints"][:12]

    # 5. 충·합·형·해·파 기반 dynamics 직접 조회
    if branch_relations or dynamics:
        _found_dynamics: list[dict] = []

        # dynamics 천간합 → 이름으로 직접 조회
        if dynamics:
            for sh in dynamics.get("stem_hap", []):
                name = sh.get("name", "")
                if name:
                    entry = _find_by_field("dynamics", "name", name)
                    if entry:
                        _found_dynamics.append(entry)

        # branch_relations 천간합
        br = branch_relations or {}
        if br.get("cheon_gan_hap"):
            for h in br["cheon_gan_hap"]:
                name = h.get("name", "")
                if name and not any(d.get("name") == name for d in _found_dynamics):
                    entry = _find_by_field("dynamics", "name", name)
                    if entry:
                        _found_dynamics.append(entry)

        result["dynamics"] = _found_dynamics[:4]

    # 6. 신강/신약 레이블 → Writer 직접 참고용
    if day_master_strength:
        result["strength"] = day_master_strength.get("level_8")

    # 7. 용신 요약 → Writer 직접 참고용
    if yong_sin:
        primary = yong_sin.get("primary", "")
        logic   = yong_sin.get("logic_type", "")
        xi_sin  = "·".join(yong_sin.get("xi_sin", []))
        result["yong_sin_summary"] = f"용신:{primary} ({logic}), 희신:{xi_sin}"

    # 8. 전체 활성 신살 상세 지식 조회 (이름 기준 중복 제거)
    if sin_sals:
        seen_names: set[str] = set()
        for ss in sin_sals:
            name = ss.get("name", "")
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            entry = _find_by_field("sin_sal", "name", name)
            if entry:
                # 같은 신살이 여러 기둥에 있을 수 있으므로 location 합산
                locations = [
                    s.get("location", []) for s in sin_sals if s.get("name") == name
                ]
                merged_locations = []
                for loc in locations:
                    if isinstance(loc, list):
                        merged_locations.extend(loc)
                    else:
                        merged_locations.append(loc)
                result["sin_sal_all"].append({
                    "name": name,
                    "priority": ss.get("priority", "low"),
                    "location": sorted(set(merged_locations)),
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
    result = _find_by_field("structure_patterns", "id", pattern_id)
    if result is None:
        result = _find_by_field("structure_patterns", "id", f"sp_{pattern_id}")
    return result


def handle_get_sin_sal_profile(sin_sal_name: str) -> dict | None:
    """신살 이름으로 전체 지식 직접 조회 (예: '역마살', '귀문관살')."""
    return _find_by_field("sin_sal", "name", sin_sal_name)
