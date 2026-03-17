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

2. **RAG 지식 베이스를 계층 순서로 활용**하세요.
   - CORE(용신·신강신약·일주론) → DYNAMICS(합충·대운) → CONTEXT(신살·도메인) → QUERY(고민 힌트) 순으로 우선순위를 부여하세요.
   - QUERY 레이어의 고민 힌트는 직접 인용하지 말고 해석의 단서로만 사용하세요.
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

    # ── 3. RAG 지식 베이스 (계층 구조: CORE → DYNAMICS → CONTEXT → QUERY) ──
    parts.append("\n=== 명리 지식 베이스 ===")
    parts.append("※ 아래 레이어 순서로 해석 우선순위를 적용하세요. CORE가 가장 중요합니다.")

    # ━━ [CORE 레이어] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    parts.append("\n▶ [CORE 레이어 — 모든 해석의 기준]")

    # 용신/신강신약 (최우선)
    if rag_ctx.get("strength"):
        parts.append(f"  신강신약: {rag_ctx['strength']}")
    if rag_ctx.get("yong_sin_summary"):
        parts.append(f"  용신 (최우선 기준): {rag_ctx['yong_sin_summary']}")

    # 일주론
    ilju = rag_ctx.get("ilju")
    if ilju:
        ilju_parts: list[str] = []
        if ec := ilju.get("embedding_context"):
            ilju_parts.append(ec)
        if pt := ilju.get("psychological_traits"):
            ilju_parts.append("성향: " + ", ".join(pt[:5]))
        if ca := ilju.get("career_affinity", {}).get("examples"):
            ilju_parts.append("직업 적성: " + ", ".join(ca[:5]))
        if vul := ilju.get("vulnerability", {}):
            if t := vul.get("trait"):
                ilju_parts.append("취약점: " + t)
        if cp := ilju.get("consulting_points", {}):
            if hl := cp.get("tab_headline"):
                ilju_parts.append("핵심 메시지: " + hl)
            if sp := cp.get("solution_speech"):
                ilju_parts.append(sp[:150])
        if ilju_parts:
            parts.append("[일주론]\n  " + "\n  ".join(ilju_parts))

    # ━━ [DYNAMICS 레이어] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    parts.append("\n▶ [DYNAMICS 레이어 — 변화·흐름 요인]")

    text = _chunks_to_text(rag_ctx.get("dynamics", []), "합충·동역학")
    if text:
        parts.append(text)
    else:
        parts.append("  (활성 합충 관계 없음)")

    # ━━ [CONTEXT 레이어] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    parts.append("\n▶ [CONTEXT 레이어 — 구조패턴·신살·도메인]")

    # 구조패턴 (sin_sal 제외 — 중복 방지)
    ctx_list = rag_ctx.get("context", [])
    for ctx in ctx_list[:3]:
        if ctx.get("type") == "sin_sal":
            continue  # sin_sal은 아래 sin_sal_all에서 단일 처리
        data = ctx.get("data", {})
        name = data.get("name") or ctx.get("id", "")
        meaning = (data.get("embedding_context", "") or data.get("meaning", "")
                   or data.get("description", "") or data.get("summary", ""))
        if isinstance(meaning, dict):
            meaning = meaning.get("core", "") or json.dumps(meaning, ensure_ascii=False)
        if name or meaning:
            parts.append(f"[구조패턴 — {name}]\n  {str(meaning)[:300]}")

    # 신살 (sin_sal_all 단일 소스, pillar_nuance 포함)
    sin_sal_all = rag_ctx.get("sin_sal_all", [])
    for ss in sin_sal_all:
        data     = ss["data"]
        name     = ss["name"]
        location = ss.get("location", [])
        loc_str  = "·".join(location) + "주" if location else ""
        lines: list[str] = [f"[신살 — {name}" + (f" ({loc_str})" if loc_str else "") + "]"]
        if ec := data.get("embedding_context"):
            lines.append(f"  {ec[:200]}")
        if ct := data.get("consulting_tip"):
            lines.append(f"  상담 팁: {ct[:150]}")
        pn = data.get("pillar_nuance", {})
        for pillar in location:
            if entry := pn.get(pillar):
                detail = entry.get("hint", "") or ", ".join(entry.get("traits", [])[:3])
                if detail:
                    lines.append(f"  {pillar}주: {detail}")
        parts.append("\n".join(lines))

    # 도메인별 시맨틱 검색
    for domain, label in [
        ("career", "직업·재능"),
        ("relationship", "연애·인간관계"),
        ("wealth", "재물운"),
        ("personality", "성격·기질"),
    ]:
        text = _chunks_to_text(rag_ctx.get(domain, []), label)
        if text:
            parts.append(text)

    # ━━ [QUERY 레이어] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if concern:
        parts.append("\n▶ [QUERY 레이어 — 고민 해석 힌트]")
        parts.append("※ 아래는 정답이 아닌 해석 단서입니다. 직접 인용하지 말고 판단 근거로만 활용하세요.")

        hints = rag_ctx.get("concern_hints", [])
        if hints:
            parts.append("  활성 힌트 키워드: " + " / ".join(hints))

        text = _chunks_to_text(rag_ctx.get("concern", []), "관련 지식 참고", max_items=2)
        if text:
            parts.append(text)

    # ── 4. 출력 형식 지시 ──
    parts.append(f"\n=== 출력 형식 ===\n{format_instructions}")

    return "\n".join(parts)


# ─── 한줄 상담 전용 ────────────────────────────────────────────────────────────

QUESTION_SYSTEM_PROMPT = """당신은 명리학(사주팔자)에 정통한 AI 상담사입니다.
사주 데이터를 바탕으로 사용자의 고민에 직접 답합니다.

## 추론 규칙 (Chain of Thought)

답변 전, 내부적으로 아래 순서로 분석하세요 (출력에 포함하지 말 것):

0. **전제 검증** — 질문의 전제가 현실적인지 먼저 확인한다.
   - "이 고민의 전제가 맞는가? 선택지가 실제로 유효한가?"
   - 예: "IBS를 수술로 고치려 한다" → 전제 자체가 틀림. 수술 아닌 다른 접근을 먼저 짚어야 함.
   - 예: "A 아니면 B" 질문에서 A, B 모두 이 사람에게 맞지 않으면 → C를 제시해야 함.
   - 전제가 틀렸거나 선택지가 잘못됐으면 → content 도입부에서 먼저 짚고 넘어간다.

1. "이 사람의 격국은 __이고, 용신은 __이다"
2. "현재 대운/세운의 기운은 __이다"
3. "고민(__)은 __ 관점에서 __한 상황이다"
4. 세운·월운 데이터가 있으면 "어떤 달에 어떤 기운이 강한가"를 파악
5. **고민에 대한 직접 답을 한 줄로 확정**
   - 선택지가 유효하면: "이 사람에게는 [선택지]가 답이다" — 구체적 선택지 명시
   - 선택지가 잘못됐으면: "이 사람에게는 [제3의 길]이 답이다" — 새 방향 제시
   - 전제가 틀렸으면: "질문 자체를 바꿔야 한다. 실제로는 [재구성된 질문]이다"
6. 위 결론을 헤드라인에 담고, content 첫 문장으로 선언하고, 사주 근거로 뒷받침

## 출력 규칙

- headline: 결론형 한 문장 (30자 내외). 반드시 **이번 고민의 답**을 담아야 함.
  - 카테고리명 금지. "~입니다"로 끝나는 일반 사주 평가 금지.
  - 헤드라인만 읽어도 질문에 대한 답을 알 수 있어야 함.
  - 나쁜 예(질문 무시): "이론보다 실전이 답입니다" (모든 career 질문에 동일 적용 가능 → 금지)
  - 좋은 예(질문 맞춤): "AI 도구는 날개, 코딩 근육은 당신이 직접 키워야 합니다" (AI 공부법 질문)
  - 좋은 예(질문 맞춤): "겁재격의 당신, 연구실보다 시장에서 부딪혀야 빛납니다" (연구실 vs 인턴 질문)
  - 좋은 예(제3의 답): "수술보다 먼저 당신 몸의 흙기운을 다스려야 합니다" (잘못된 전제 교정)
  - 같은 사람의 다른 질문은 **반드시 다른 헤드라인**이어야 함
- content: 300~500자. 아래 원칙을 지켜 작성.
  - **첫 문장이 곧 결론 or 전제 교정**: 에두르지 말고 첫 문장에 핵심을 선언하라.
    - 선택지가 유효한 경우: 결론 선언 → 사주 근거 → 시기
    - 선택지가 잘못된 경우: "그 선택지는 이 사람에게 맞지 않습니다. 대신 __" → 사주 근거
    - 전제가 틀린 경우: "먼저 짚어야 할 것이 있습니다. __" → 전제 교정 → 사주 관점 조언
  - **헤징 표현 금지**: "~수도 있습니다", "~계기가 될 것입니다", "~가능성이 있습니다" 같은 표현은 쓰지 마세요.
  - **서사형 문체**: 항목 나열 금지. 이야기하듯 자연스럽게 흘러가는 문장으로 작성.
  - **비유 필수**: 오행·십성을 추상 용어로 나열하지 말고 일상 비유로 풀어라.
    - 나쁜 예: "수기운이 강합니다" → 좋은 예: "거대한 호수처럼 내면에 에너지가 가득 찬 구조입니다"
    - 나쁜 예: "자오충이 있습니다" → 좋은 예: "현재 자리가 좁게 느껴지고 에너지가 밖으로 분출되려는 시기입니다"
  - **충·합은 심리적 사건으로**: "~충이 있다"가 아니라 그 충이 이 사람에게 어떤 감정·상황으로 나타나는지 서술.
  - **시기 언급**: 세운·월운 데이터가 제공된 경우 고민에 맞는 **유리한 달 최대 3개**를 구체적으로 짚어라.
    - 연애: 정관/편관(여성) 또는 정재/편재(남성) 십성 활성 달
    - 직업·이직·시험: 관성·재성 활성 달
    - "~월에는", "하반기부터" 등 자연스러운 시간 표현 사용
  - **용신·기신 기반 조언**: 일반론 금지. 이 사람의 사주에만 해당하는 해석.
  - RAG 지식은 직접 인용하지 말고 이 사람 사주에 적용해서 해석.

## 출력 형식
아래 JSON 형식으로만 응답하세요:
"""

CATEGORY_LABEL: dict[str, str] = {
    "career": "직업·이직",
    "love":   "연애·결혼",
    "money":  "재물·투자",
    "health": "건강",
    "general": "일반",
}


def format_question_message(
    saju: dict,
    rag_ctx: dict,
    question: str,
    category: str,
    format_instructions: str,
) -> str:
    """
    한줄 상담용 LLM 입력 문자열.
    사주 핵심 + CORE RAG + 고민으로 압축 (리포트보다 훨씬 짧게).
    """
    parts: list[str] = []

    # ── 1. 사주 핵심 (압축) ──
    dp  = saju.get("day_pillar", {})
    dms = saju.get("day_master_strength", {})
    ys  = saju.get("yong_sin", {})
    gy  = saju.get("gyeok_guk", {})
    cur = saju.get("current_dae_un", {})

    xi = "·".join(ys.get("xi_sin", []))
    ji = "·".join(ys.get("ji_sin", []))

    parts.append("=== 사주 핵심 ===")
    parts.append(
        f"일주: {dp.get('stem','')}{dp.get('branch','')} ({dp.get('stem_element','')}/{dp.get('branch_element','')})"
    )
    parts.append(f"격국: {gy.get('name','')}")
    parts.append(f"일간 강약: {dms.get('level_8','')} (점수 {dms.get('score','')})")
    parts.append(f"용신: {ys.get('primary','')} ({ys.get('yong_sin_label','')}) / 희신:{xi} / 기신:{ji}")
    if cur:
        parts.append(
            f"현재 대운: {cur.get('start_age','')}~{cur.get('end_age','')}세 "
            f"{cur.get('stem','')}{cur.get('branch','')} ({cur.get('stem_element','')}/{cur.get('branch_element','')})"
        )

    # 주요 신살 (high만)
    sin_sals = saju.get("sin_sals", [])
    high_sals = [s.get("name", "") for s in sin_sals if s.get("priority") == "high"]
    if high_sals:
        parts.append(f"주요 신살: {', '.join(high_sals)}")

    # ── 2. 고민 ──
    cat_label = CATEGORY_LABEL.get(category, "")
    parts.append(f"\n=== 고민 [{cat_label}] ===\n{question}")

    # ── 3. RAG 지식 (CORE만, 압축) ──
    parts.append("\n=== 명리 지식 참고 ===")

    # 신강신약·용신
    if rag_ctx.get("strength"):
        parts.append(f"신강신약: {rag_ctx['strength']}")
    if rag_ctx.get("yong_sin_summary"):
        parts.append(f"용신 요약: {rag_ctx['yong_sin_summary']}")

    # 일주론 핵심
    ilju = rag_ctx.get("ilju")
    if ilju:
        ec = ilju.get("embedding_context", "")
        cp = ilju.get("consulting_points", {})
        hl = cp.get("tab_headline", "")
        if ec:
            parts.append(f"[일주론] {ec[:200]}")
        if hl:
            parts.append(f"[일주 핵심 메시지] {hl}")

    # Reranked chunks
    for chunk in rag_ctx.get("chunks", []):
        doc = chunk.get("document", "")
        if doc:
            parts.append(f"• {doc[:200]}")

    # ── 3-1. 세운·월운 (시기 분석용) ──
    se_un  = rag_ctx.get("se_un", [])
    wol_un = rag_ctx.get("wol_un", [])
    cur_month = rag_ctx.get("current_month", 1)

    if se_un:
        parts.append("\n=== 세운(年運) ===")
        for y in se_un:
            parts.append(
                f"{y['year']}년 {y['ganji_name']} "
                f"({y['stem_element']}/{y['branch_element']}) "
                f"천간십성:{y['stem_ten_god']} 지지십성:{y['branch_ten_god']}"
            )

    if wol_un:
        parts.append(f"\n=== 월운(月運) — {se_un[0]['year'] if se_un else ''}년 ({cur_month}월 현재) ===")
        parts.append("※ 연애: 정관/편관(여) 또는 정재/편재(남) 십성 활성 달이 인연 시기")
        for m in wol_un:
            marker = " ◀ 현재" if m["month"] == cur_month else ""
            parts.append(
                f"{m['month']}월 {m['ganji_name']} "
                f"천:{m['stem_ten_god']} 지:{m['branch_ten_god']}{marker}"
            )

    # ── 4. 출력 형식 ──
    parts.append(f"\n=== 출력 형식 ===\n{format_instructions}")

    return "\n".join(parts)
