"""
Writer LLM 프롬프트 구성.

- SYSTEM_PROMPT  : 페르소나·출력 규칙 (불변)
- format_user_message() : saju + rag_ctx + concern → 사용자 메시지 문자열
"""

from __future__ import annotations
import json


# ─── 시스템 프롬프트 ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """당신은 명리학(사주팔자)에 정통한 AI 상담사입니다.
주어진 사주 분석 데이터와 명리 지식 베이스(RAG 청크)를 바탕으로,
오직 이 사람만을 위한 결론형 리포트를 작성합니다.

## 핵심 원칙

1. **헤드라인은 반드시 결론형 문장**으로 작성하세요.
   - 나쁜 예: "재물운 분석", "성격 분야"
   - 좋은 예: "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자"

2. **내용은 RAG 지식 베이스에 근거**하여 작성하세요.
   - 제공된 RAG 청크의 해석을 이 사람의 사주에 맞게 적용하세요.
   - 근거 없는 추측이나 일반론은 피하세요.

3. **사용자의 고민이 있다면 우선적으로 반영**하세요.
   - 고민과 관련된 탭을 반드시 포함하세요.
   - 고민에 대한 직접적인 통찰을 헤드라인에 담으세요.

4. **10개 탭**을 생성하세요 (고민이 있으면 1개 고민 탭 포함).
   - 성격/기질, 직업/재능, 재물운, 연애/결혼, 건강, 대운 흐름, 현재 시기 조언 등 다양하게 구성
   - 탭마다 독자적인 통찰이 있어야 합니다

5. **문체**: 친근하지만 권위 있는 상담사 말투. 존댓말 사용.
   내용은 200~400자 내외로 핵심만 담아 작성하세요.

## 출력 형식
아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
"""


# ─── 사주 프로파일 포맷터 ─────────────────────────────────────────────────────

def _pillar_str(p: dict) -> str:
    if not p:
        return "?"
    return (
        f"{p.get('stem','')}{p.get('branch','')} "
        f"({p.get('stem_element','')}/{p.get('branch_element','')})"
        f" 십성:{p.get('stem_ten_god','')}/{p.get('branch_ten_god','')}"
        f" {p.get('twelve_wun','')}"
    )


def _chunks_to_text(chunks: list[dict], label: str, max_items: int = 3) -> str:
    if not chunks:
        return ""
    lines = [f"[{label}]"]
    for c in chunks[:max_items]:
        doc = c.get("document", "")
        if doc:
            lines.append(f"  • {doc[:300]}")
    return "\n".join(lines)


def format_user_message(
    saju: dict,
    rag_ctx: dict,
    concern: str | None,
    format_instructions: str,
) -> str:
    """
    사주 계산 결과 + RAG 컨텍스트 + 고민을 Writer LLM 입력 문자열로 변환.
    """
    parts: list[str] = []

    # ── 1. 기본 사주 프로파일 ──
    meta   = saju.get("meta", {})
    dms    = saju.get("day_master_strength", {})
    ys     = saju.get("yong_sin", {})
    gyeok  = saju.get("gyeok_guk", {})

    parts.append("=== 사주 프로파일 ===")
    parts.append(f"생년월일시: {meta.get('birth_date','')} {meta.get('birth_time','')} ({meta.get('gender','')})")
    parts.append(f"연주: {_pillar_str(saju.get('year_pillar',{}))}")
    parts.append(f"월주: {_pillar_str(saju.get('month_pillar',{}))}")
    parts.append(f"일주: {_pillar_str(saju.get('day_pillar',{}))}")
    parts.append(f"시주: {_pillar_str(saju.get('hour_pillar',{}))}")

    # 일간 강약
    parts.append(
        f"일간 강약: {dms.get('level_8','')} (점수 {dms.get('score','')})"
        f" / 득령:{dms.get('deuk_ryeong','')} 득지:{dms.get('deuk_ji','')} 득시:{dms.get('deuk_si','')} 득세:{dms.get('deuk_se','')}"
    )

    # 용신
    xi = "·".join(ys.get("xi_sin", []))
    ji = "·".join(ys.get("ji_sin", []))
    parts.append(
        f"용신: {ys.get('primary','')} ({ys.get('yong_sin_label','')}) / 희신:{xi} / 기신:{ji}"
    )

    # 격국
    parts.append(f"격국: {gyeok.get('name','')} — {gyeok.get('description','')}")

    # 오행 분포 (기본 + 합화 적용)
    wuxing     = saju.get("wuxing_count", {})
    wuxing_hap = saju.get("wuxing_count_hap", {})
    wuxing_str = " ".join(f"{k}:{v:.0f}%" for k, v in wuxing.items())
    parts.append(f"오행 분포(원래): {wuxing_str}")

    # 합화로 변화된 오행이 있을 때만 표시
    if wuxing_hap and wuxing_hap != wuxing:
        hap_str = " ".join(f"{k}:{v:.0f}%" for k, v in wuxing_hap.items())
        parts.append(f"오행 분포(합화후): {hap_str}")

    # 지지 관계 (충·합·형·해·파) 사람이 읽기 좋은 형태로
    br = saju.get("branch_relations", {})
    br_lines: list[str] = []

    for hap in br.get("yuk_hap", []):
        pair = "·".join(hap.get("pair", []))
        elem = hap.get("element", "")
        eff  = hap.get("is_effective", False)
        status = "합화 성립" if eff else "합화 불성립(충·극 방해)"
        br_lines.append(f"육합 {pair}→{elem}화 ({status})")

    sam_hap = br.get("sam_hap")
    if sam_hap:
        branches = "·".join(sam_hap.get("branches", []))
        elem = sam_hap.get("element", "")
        br_lines.append(f"삼합 {branches}→{elem}화")

    for pair in br.get("chung", []):
        br_lines.append(f"충 {'↔'.join(pair)} (충돌·약화)")

    for hyeong in br.get("sam_hyeong", []):
        br_lines.append(f"형 {hyeong}")

    for pair in br.get("pa", []):
        br_lines.append(f"파 {'·'.join(pair)}")

    for pair in br.get("hae", []):
        br_lines.append(f"해 {'·'.join(pair)}")

    if br_lines:
        parts.append("지지 상호작용: " + " / ".join(br_lines))

    # 십성 분포
    tgd = saju.get("ten_gods_distribution", {})
    if tgd:
        tgd_str = " ".join(f"{k}:{v:.0f}%" for k, v in sorted(tgd.items(), key=lambda x: -x[1]))
        parts.append(f"십성 분포: {tgd_str}")

    # 신살
    sin_sals = saju.get("sin_sals", [])
    if sin_sals:
        sal_names = [s.get("name", "") for s in sin_sals if s.get("priority") in ("high", "medium")]
        if sal_names:
            parts.append(f"주요 신살: {', '.join(sal_names)}")

    # 현재 대운
    cur_dae_un = saju.get("current_dae_un", {})
    if cur_dae_un:
        parts.append(
            f"현재 대운: {cur_dae_un.get('start_age','')}~{cur_dae_un.get('end_age','')}세 "
            f"{cur_dae_un.get('stem','')}{cur_dae_un.get('branch','')} "
            f"({cur_dae_un.get('stem_element','')}/{cur_dae_un.get('branch_element','')})"
        )

    # 행동 프로파일
    bp = saju.get("behavior_profile", [])
    if bp:
        parts.append(f"행동 프로파일: {', '.join(bp[:6])}")

    # ── 2. 사용자 고민 ──
    if concern:
        parts.append(f"\n=== 사용자 고민 ===\n{concern}")

    # ── 3. RAG 지식 베이스 ──
    parts.append("\n=== 명리 지식 베이스 (참고용) ===")

    # 일주론
    ilju = rag_ctx.get("ilju")
    if ilju:
        meaning = ilju.get("meaning", "")
        if isinstance(meaning, dict):
            meaning = meaning.get("core", "")
        parts.append(f"[일주론]\n  {str(meaning)[:400]}")

    # 컨텍스트 직접 조회 (구조패턴·신살)
    ctx_list = rag_ctx.get("context", [])
    for ctx in ctx_list[:3]:
        data = ctx.get("data", {})
        name = data.get("name") or ctx.get("id", "")
        meaning = data.get("meaning", "") or data.get("description", "") or data.get("summary", "")
        if isinstance(meaning, dict):
            meaning = meaning.get("core", "") or json.dumps(meaning, ensure_ascii=False)
        if name or meaning:
            parts.append(f"[{ctx.get('type','')} — {name}]\n  {str(meaning)[:300]}")

    # 도메인별 시맨틱 검색 결과
    for domain, label in [
        ("career", "직업·재능"),
        ("relationship", "연애·인간관계"),
        ("wealth", "재물운"),
        ("personality", "성격·기질"),
    ]:
        text = _chunks_to_text(rag_ctx.get(domain, []), label)
        if text:
            parts.append(text)

    # 고민 관련 RAG
    if concern:
        text = _chunks_to_text(rag_ctx.get("concern", []), "고민 관련")
        if text:
            parts.append(text)

    # 동역학 RAG
    text = _chunks_to_text(rag_ctx.get("dynamics", []), "합충·동역학")
    if text:
        parts.append(text)

    # 신강/신약·용신 요약 (메타데이터)
    if rag_ctx.get("strength"):
        parts.append(f"[신강신약 참고] {rag_ctx['strength']}")
    if rag_ctx.get("yong_sin_summary"):
        parts.append(f"[용신 참고] {rag_ctx['yong_sin_summary']}")

    # ── 4. 출력 형식 지시 ──
    parts.append(f"\n=== 출력 형식 ===\n{format_instructions}")

    return "\n".join(parts)
