"""
사주 구조 패턴(Structure Patterns) 감지 — v2.4

설계 원칙:
  check   → Dist + Level  (十星 기반 구조 판단)
  tag_fn  → Dist + Level + WuxingPct  (오행 맥락 기반 해석 태그)

개선사항:
  - check/tag_fn 역할 분리: 구조(십성) vs 해석방향(오행)
  - exclusive_group: 종격 등 고우선순위 패턴이 같은 그룹 내 하위 패턴 차단
  - categories: list[str] (multi-label) — RAG 카테고리 필터 + UI 필터 지원
  - PatternRegistry 카테고리 인덱스: 패턴 100개 대비 O(1) 검색
  - tag_fn 전량 동적화: static tags 폐기
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


# ─── 타입 ────────────────────────────────────────────────────────

Dist      = dict[str, float]          # 십성 분포 퍼센트 (총합 ~100)
Level     = str                       # "very_weak"|"weak"|"neutral"|"strong"|"very_strong"
WuxingPct = dict[str, float]          # 오행 퍼센트 (목/화/토/금/수)
CheckFn   = Callable[[Dist, Level], bool]                          # 十星 중심
TagFn     = Callable[[Dist, Level, WuxingPct], list[str]]          # 오행 중심


# ─── Pattern 데이터클래스 ────────────────────────────────────────

@dataclass
class Pattern:
    id:              str
    name:            str
    hanja:           str
    priority:        int              # 0-100 (높을수록 핵심)
    categories:      list[str]        # multi-label: wealth | power | expression | identity | balance
    check:           CheckFn = field(repr=False)
    tag_fn:          TagFn = field(repr=False)
    exclusive_group: str | None = None   # 같은 그룹 내 낮은 우선순위 패턴 차단


# ─── 헬퍼 ───────────────────────────────────────────────────────

def _g(dist: Dist, *keys: str) -> float:
    return sum(dist.get(k, 0.0) for k in keys)

def _dom(wx: WuxingPct) -> str | None:
    return max(wx, key=wx.get) if wx else None

def _is_weak(lv: Level) -> bool:
    return lv in ("weak", "very_weak")

def _is_strong(lv: Level) -> bool:
    return lv in ("strong", "very_strong")


# ─── Tag Functions (동적, 오행 맥락 반영) ────────────────────────

def _tf_sig_sang_saeng_jae(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    """식상생재: 어떤 오행의 식상인가에 따라 수익 유형 분화."""
    element_tags = {
        "화": ["creative_content_income", "entertainer_wealth", "visibility_monetization"],
        "금": ["technical_product_income", "precision_craft_wealth", "quality_driven_profit"],
        "목": ["educational_service_income", "growth_content_wealth", "nurture_to_revenue"],
        "수": ["intellectual_product_income", "research_monetization", "insight_sells"],
        "토": ["stable_skill_income", "craft_business_wealth", "reliable_trade_profit"],
    }
    base = ["idea_to_income", "execution_converts", "creative_monetization"]
    return base + element_tags.get(_dom(wx), ["general_idea_income"])


def _tf_jae_da_sin_yak(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    """재다신약: 재성 과다 유형 + 신약 정도에 따라 조언 분화."""
    base = ["opportunity_overload", "need_focus", "greed_trap_warning"]
    if lv == "very_weak":
        return base + ["critical_energy_depletion", "rest_first_strategy"]
    return base + ["choose_one_opportunity", "energy_management_essential"]


def _tf_gun_gyeop_jaeng_jae(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    """군겁쟁재: 겁재 우세 vs 비견 우세에 따라 경쟁 방식 분화."""
    base = ["competitive_field", "solo_outperforms", "partnership_risk"]
    if d.get("겁재", 0) > d.get("비견", 0):
        return base + ["aggressive_rival_pattern", "external_conflict_prone"]
    return base + ["peer_competition", "internal_parallel_pursuit"]


def _tf_gwan_in_sang_saeng(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    """관인상생: 정관 vs 편관 비율로 성장 경로 분화."""
    base = ["institution_growth", "systematic_advance", "learning_loop"]
    if d.get("정관", 0) >= d.get("편관", 0):
        return base + ["credential_career", "stable_promotion_track"]
    return base + ["pressure_driven_growth", "merit_through_adversity"]


def _tf_sig_sin_je_sal(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    """식신제살: 식신 vs 상관 우세에 따라 대처 스타일 분화."""
    base = ["creative_resilience", "crisis_turnaround", "pressure_to_innovation"]
    if d.get("상관", 0) > d.get("식신", 0):
        return base + ["sharp_rebuttal_style", "confrontational_creativity"]
    return base + ["humor_diffusion_style", "soft_power_against_pressure"]


def _tf_sal_in_sang_saeng(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["pressure_to_growth", "adversity_skill", "tough_env_thrives",
            "hardship_accelerates", "pain_becomes_expertise"]


def _tf_sang_gwan_pae_in(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    base = ["critical_wisdom", "intellectual_rebel", "evidence_based_critique"]
    dom = _dom(wx)
    if dom == "금":
        return base + ["analytical_sharp_mind", "precise_argumentation"]
    if dom == "수":
        return base + ["deep_theoretical_critique", "philosophical_challenger"]
    return base + ["sharp_with_knowledge", "creative_contrarian"]


def _tf_in_da_sin_gang(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["knowledge_rich", "action_deficit", "theory_over_experience",
            "sheltered_growth", "independence_practice_needed"]


def _tf_gwan_sal_hon_jap(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["authority_conflict", "direction_confusion", "dual_standard",
            "mixed_pressure_sources", "clarify_one_goal"]


def _tf_jae_gwan_ssang_mi(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["wealth_honor_balance", "career_and_money_aligned",
            "dual_aspiration_fulfilled", "establishment_success_pattern"]


def _tf_sig_sang_tae_gwa(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    base = ["expression_overflow", "scattered_energy", "output_without_intake"]
    dom = _dom(wx)
    if dom == "화":
        return base + ["emotional_burnout_risk", "fame_without_foundation"]
    return base + ["needs_grounding", "creative_exhaustion_warning"]


def _tf_bi_gyeop_tae_gwa(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["independence_extreme", "hard_to_compromise", "lone_wolf",
            "self_reliance_strength", "collaboration_friction"]


# 종격 tag functions
def _tf_jong_wang(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["extreme_self_energy", "near_invincible_identity", "solo_only",
            "all_in_independence", "conventional_advice_irrelevant"]


def _tf_jong_jae(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["full_wealth_structure", "money_centered_life",
            "opportunity_magnet", "material_world_navigator", "wealth_is_self"]


def _tf_jong_sal(d: Dist, lv: Level, wx: WuxingPct) -> list[str]:
    return ["authority_total_surrender", "institution_maximum",
            "discipline_extreme", "hierarchy_aligned", "system_absorbed"]


# ─── PatternRegistry (카테고리 인덱스 포함) ──────────────────────

class PatternRegistry:
    _patterns:    list[Pattern] = []
    _by_category: dict[str, list[Pattern]] = {}

    @classmethod
    def register(cls, p: Pattern) -> Pattern:
        cls._patterns.append(p)
        for cat in p.categories:
            cls._by_category.setdefault(cat, []).append(p)
        return p

    @classmethod
    def detect(
        cls,
        dist:       Dist,
        level:      Level,
        wuxing_pct: WuxingPct | None = None,
        categories: list[str] | None = None,
    ) -> list[dict]:
        """
        구조 패턴 감지.

        Args:
            dist       : ten_gods_distribution (퍼센트, 총합 100)
            level      : day_master_strength.level
            wuxing_pct : 오행 퍼센트 분포 (tag_fn에서 맥락 활용)
            categories : 검사할 카테고리 목록 (None = 전체 검사)

        Returns:
            [{"id", "name", "hanja", "priority", "categories", "tags"}, ...]
            priority 내림차순 정렬. RAG 전달 시 상위 2개 우선 활용.
        """
        wx = wuxing_pct or {}

        # 카테고리 인덱스 활용 (O(N) → 카테고리별 소규모 풀 검사)
        if categories:
            pool: dict[str, Pattern] = {}
            for cat in categories:
                for p in cls._by_category.get(cat, []):
                    pool.setdefault(p.id, p)
            candidates = list(pool.values())
        else:
            candidates = cls._patterns

        # 1. check: Dist + Level 기반 (十星 구조 판단)
        matched = [p for p in candidates if p.check(dist, level)]

        # 2. priority 내림차순 정렬
        matched.sort(key=lambda p: p.priority, reverse=True)

        # 3. mutual exclusion via exclusive_group
        #    같은 그룹 내 첫 번째(고우선순위) 패턴만 통과
        final: list[Pattern] = []
        seen_groups: set[str] = set()
        for p in matched:
            if p.exclusive_group and p.exclusive_group in seen_groups:
                continue
            final.append(p)
            if p.exclusive_group:
                seen_groups.add(p.exclusive_group)

        # 4. tag_fn: Dist + Level + WuxingPct 기반 (오행 맥락 해석 태그)
        return [
            {
                "id":         p.id,
                "name":       p.name,
                "hanja":      p.hanja,
                "priority":   p.priority,
                "categories": p.categories,
                "tags":       p.tag_fn(dist, level, wx),
            }
            for p in final
        ]


# ─── 패턴 등록 ───────────────────────────────────────────────────
# 특수 종격(priority 90+) → 핵심(70~89) → 표준(50~69) → 보조(30~49)

# ── 특수 종격 구조 — exclusive_group="special_jong" ─────────────

# ── 특수 종격 구조 (priority 90+) ─────────────────────────────
# exclusive_group 설계:
#   "비겁_dominant": 종왕(95) > 군겁쟝재(75) > 비겁태과(55)
#   "재성_dominant": 종재(95) > 재다신약(80)
#   "관성_dominant": 종살(95) > 관인상생(70) > 살인상생(65) > 관살혼잡(45)
# 같은 그룹 내 가장 높은 priority 패턴이 감지되면 하위 패턴은 차단됨.

PatternRegistry.register(Pattern(
    id              = "jong_wang_pattern",
    name            = "종왕 구조",
    hanja           = "從旺構造",
    priority        = 95,
    categories      = ["identity"],
    check           = lambda d, lv: _g(d, "비견", "겁재") >= 55 and _is_strong(lv),
    tag_fn          = _tf_jong_wang,
    exclusive_group = "비겁_dominant",
))

PatternRegistry.register(Pattern(
    id              = "jong_jae_pattern",
    name            = "종재 구조",
    hanja           = "從財構造",
    priority        = 95,
    categories      = ["wealth"],
    check           = lambda d, lv: _g(d, "편재", "정재") >= 55,
    tag_fn          = _tf_jong_jae,
    exclusive_group = "재성_dominant",
))

PatternRegistry.register(Pattern(
    id              = "jong_sal_pattern",
    name            = "종살 구조",
    hanja           = "從殺構造",
    priority        = 95,
    categories      = ["power"],
    check           = lambda d, lv: _g(d, "편관", "정관") >= 55,
    tag_fn          = _tf_jong_sal,
    exclusive_group = "관성_dominant",
))

# ── 핵심 구조 패턴 (priority 70~89) ─────────────────────────────

PatternRegistry.register(Pattern(
    id              = "jae_da_sin_yak",
    name            = "재다신약",
    hanja           = "財多身弱",
    priority        = 80,
    categories      = ["wealth", "balance"],
    check           = lambda d, lv: _g(d, "편재", "정재") > 30 and _is_weak(lv),
    tag_fn          = _tf_jae_da_sin_yak,
    exclusive_group = "재성_dominant",
))

PatternRegistry.register(Pattern(
    id              = "gun_gyeop_jaeng_jae",
    name            = "군겁쟁재",
    hanja           = "群劫爭財",
    priority        = 75,
    categories      = ["identity", "wealth"],
    check           = lambda d, lv: _g(d, "비견", "겁재") > 25 and _g(d, "편재", "정재") < 15,
    tag_fn          = _tf_gun_gyeop_jaeng_jae,
    exclusive_group = "비겁_dominant",
))

PatternRegistry.register(Pattern(
    id         = "sig_sang_saeng_jae",
    name       = "식상생재",
    hanja      = "食傷生財",
    priority   = 70,
    categories = ["wealth", "expression"],
    check      = lambda d, lv: _g(d, "식신", "상관") > 10 and _g(d, "편재", "정재") > 15,
    tag_fn     = _tf_sig_sang_saeng_jae,
))

PatternRegistry.register(Pattern(
    id              = "gwan_in_sang_saeng",
    name            = "관인상생",
    hanja           = "官印相生",
    priority        = 70,
    categories      = ["power", "balance"],
    check           = lambda d, lv: _g(d, "편관", "정관") > 10 and _g(d, "편인", "정인") > 10,
    tag_fn          = _tf_gwan_in_sang_saeng,
    exclusive_group = "관성_dominant",
))

# ── 표준 구조 패턴 (priority 50~69) ─────────────────────────────

PatternRegistry.register(Pattern(
    id         = "sig_sin_je_sal",
    name       = "식신제살",
    hanja      = "食神制殺",
    priority   = 65,
    categories = ["expression", "power"],
    check      = lambda d, lv: d.get("식신", 0) > 5 and d.get("편관", 0) > 5,
    tag_fn     = _tf_sig_sin_je_sal,
))

PatternRegistry.register(Pattern(
    id              = "sal_in_sang_saeng",
    name            = "살인상생",
    hanja           = "殺印相生",
    priority        = 65,
    categories      = ["power"],
    check           = lambda d, lv: d.get("편관", 0) > 15 and _g(d, "편인", "정인") > 15,
    tag_fn          = _tf_sal_in_sang_saeng,
    exclusive_group = "관성_dominant",
))

PatternRegistry.register(Pattern(
    id         = "sang_gwan_pae_in",
    name       = "상관패인",
    hanja      = "傷官佩印",
    priority   = 60,
    categories = ["expression", "power"],
    check      = lambda d, lv: d.get("상관", 0) > 5 and _g(d, "편인", "정인") > 10,
    tag_fn     = _tf_sang_gwan_pae_in,
))

PatternRegistry.register(Pattern(
    id         = "in_da_sin_gang",
    name       = "인다신강",
    hanja      = "印多身强",
    priority   = 60,
    categories = ["power", "balance"],
    check      = lambda d, lv: _g(d, "편인", "정인") > 30 and _is_strong(lv),
    tag_fn     = _tf_in_da_sin_gang,
))

PatternRegistry.register(Pattern(
    id         = "jae_gwan_ssang_mi",
    name       = "재관쌍미",
    hanja      = "財官雙美",
    priority   = 55,
    categories = ["wealth", "power", "balance"],
    check      = lambda d, lv: (
        _g(d, "편재", "정재") >= 15
        and _g(d, "편관", "정관") >= 15
        and not _is_weak(lv)
    ),
    tag_fn     = _tf_jae_gwan_ssang_mi,
))

PatternRegistry.register(Pattern(
    id              = "bi_gyeop_tae_gwa",
    name            = "비겁태과",
    hanja           = "比劫太過",
    priority        = 55,
    categories      = ["identity"],
    check           = lambda d, lv: _g(d, "비견", "겁재") > 40 and _is_strong(lv),
    tag_fn          = _tf_bi_gyeop_tae_gwa,
    exclusive_group = "비겁_dominant",
))

# ── 보조 구조 패턴 (priority 30~49) ─────────────────────────────

PatternRegistry.register(Pattern(
    id         = "sig_sang_tae_gwa",
    name       = "식상태과",
    hanja      = "食傷太過",
    priority   = 50,
    categories = ["expression"],
    check      = lambda d, lv: _g(d, "식신", "상관") > 40,
    tag_fn     = _tf_sig_sang_tae_gwa,
))

PatternRegistry.register(Pattern(
    id              = "gwan_sal_hon_jap",
    name            = "관살혼잡",
    hanja           = "官殺混雜",
    priority        = 45,
    categories      = ["power"],
    check           = lambda d, lv: d.get("편관", 0) > 0 and d.get("정관", 0) > 0,
    tag_fn          = _tf_gwan_sal_hon_jap,
    exclusive_group = "관성_dominant",
))


# ─── 공개 API ───────────────────────────────────────────────────

def detect_structure_patterns(
    ten_gods_dist_pct: Dist,
    strength_level:    Level,
    wuxing_pct:        WuxingPct | None = None,
) -> list[dict]:
    """
    구조 패턴 감지 — 공개 진입점.

    Args:
        ten_gods_dist_pct : ten_gods_distribution (퍼센트, 총합 100)
        strength_level    : day_master_strength.level
        wuxing_pct        : 오행 퍼센트 (오행 맥락 태그에 활용, optional)

    Returns:
        [{"id", "name", "hanja", "priority", "categories", "tags"}, ...]
        priority 내림차순. RAG 전달 시 priority ≥ 60인 상위 2개 권장.
    """
    return PatternRegistry.detect(ten_gods_dist_pct, strength_level, wuxing_pct)
