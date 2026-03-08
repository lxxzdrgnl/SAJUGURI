"""
calculate_saju MCP tool 핸들러.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from lib.saju import calculate_saju as _calc
from lib.ten_gods import generate_ten_gods_list, calculate_ten_gods_distribution, calculate_ten_god, get_branch_ten_god
from lib.sin_sal import find_sin_sals
from lib.day_master_strength import analyze_day_master_strength
from lib.gyeok_guk import determine_gyeok_guk
from lib.yong_sin import select_yong_sin
from lib.dae_un import calculate_dae_un
from lib.twelve_wun import get_twelve_wun
from lib.validation import validate_birth_input
from data.heavenly_stems import STEMS_BY_KOREAN
from data.timezone_history import get_solar_correction_minutes, get_historical_note
from data.wuxing import WUXING_GENERATION, WUXING_DESTRUCTION
from data.earthly_branches import SAM_HYEONG as _SAM_HYEONG
from lib.structure_patterns import detect_structure_patterns
from lib.dynamics import build_dynamics
from lib.synergy import compute_synergy_tags
from lib.behavior_synthesizer import synthesize_behavior_profile
from lib.context_ranker import rank_context
from lib.life_domain_mapper import map_life_domains

# sin_sal type → priority
_SAL_PRIORITY: dict[str, str] = {
    "lucky": "medium",
    "neutral": "low",
    "unlucky": "high",
    "warning": "high",
}


def handle_calculate_saju(
    birth_date: str,
    birth_time: str,
    gender: str,
    calendar: str = "solar",
    is_leap_month: bool = False,
) -> dict:
    """
    사주팔자 전체 계산 — Pipeline 패턴.
    각 단계의 결과가 다음 단계의 입력으로 연결됨.
    """
    validate_birth_input(birth_date, birth_time, gender, calendar)

    # 1. 4기둥 계산
    saju = _calc(birth_date, birth_time, gender, calendar, is_leap_month)
    day_stem = saju["day_pillar"]["stem"]

    # 2. 각 기둥에 십성 + 12운성 추가
    ten_gods_list = generate_ten_gods_list(saju)
    pillars_enriched = {}
    for i, key in enumerate(["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]):
        p = saju[key]
        pillars_enriched[key] = {
            **p,
            "stem_ten_god": ten_gods_list[i],
            "branch_ten_god": get_branch_ten_god(day_stem, p["branch"]),
            "twelve_wun": get_twelve_wun(p["stem"], p["branch"]),
        }

    ten_gods_dist = calculate_ten_gods_distribution(saju)

    # 3. 신살 + priority 태그
    sin_sals = [
        {**s, "priority": _SAL_PRIORITY.get(s["type"], "low")}
        for s in find_sin_sals(saju)
    ]

    # 4. 일간 강약
    strength = analyze_day_master_strength(saju, ten_gods_dist)

    # 5. 격국
    gyeok_guk = determine_gyeok_guk(ten_gods_dist)

    # 6. 용신
    yong_sin = select_yong_sin(saju, strength, ten_gods_dist)

    # 7. 현재 대운
    dae_un_list = calculate_dae_un(saju, count=10)
    birth_year = int(birth_date.split("-")[0])
    current_age = datetime.now().year - birth_year
    current_dae_un = next(
        (d for d in dae_un_list if d["start_age"] <= current_age <= d["end_age"]),
        dae_un_list[-1],
    )
    current_dae_un = {
        **current_dae_un,
        "stem_ten_god": calculate_ten_god(day_stem, current_dae_un["stem"]),
        "branch_ten_god": get_branch_ten_god(day_stem, current_dae_un["branch"]),
    }

    # 8. 음양 비율
    all_stems = [saju[k]["stem"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    all_branches_yy = [saju[k]["yin_yang"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    stem_yy = [STEMS_BY_KOREAN[s]["yin_yang"] for s in all_stems]
    branch_yy = all_branches_yy  # branch yin_yang = stem yin_yang of branch's rep stem (simplified: use pillar yin_yang)
    all_yy = stem_yy + [saju[k]["yin_yang"] for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]]
    yang_count = sum(1 for y in all_yy if y == "양")
    yin_count = 8 - yang_count
    yin_yang_ratio = {
        "yang": round(yang_count / 8 * 100, 1),
        "yin": round(yin_count / 8 * 100, 1),
    }

    # 9. meta
    hh, mm = map(int, birth_time.split(":"))
    original_dt = datetime(birth_year, *map(int, birth_date.split("-")[1:]), hh, mm)
    correction = get_solar_correction_minutes(original_dt)
    applied_dt = original_dt + timedelta(minutes=correction)
    meta = {
        "time_correction_minutes": correction,
        "applied_time": applied_dt.strftime("%Y-%m-%dT%H:%M"),
        "timezone_note": get_historical_note(original_dt),
    }

    # 빈 필드 제거: null·빈 리스트 키 제외
    branch_rel = {k: v for k, v in saju["branch_relations"].items() if v}

    # 육합 is_effective: 충·형·파 간섭 검사 (충이 있으면 합 파괴)
    _interference_sets: dict[str, set[str]] = {
        "chung": {b for pair in saju["branch_relations"].get("chung", []) for b in pair},
        "hyung": {b for name in saju["branch_relations"].get("sam_hyeong", []) for b in _SAM_HYEONG.get(name, [])},
        "hae":   {b for pair in saju["branch_relations"].get("yuk_hae", []) for b in pair},
    }
    if "yuk_hap" in branch_rel:
        def _yuk_hap_entry(h: dict) -> dict:
            pair = h["pair"]
            found = [t for t, s in _interference_sets.items() if any(b in s for b in pair)]
            broken = "chung" in found  # 충만 합 파괴, 형·파는 약화 참고
            return {**h, "is_effective": not broken, "interference_factors": found}
        branch_rel["yuk_hap"] = [_yuk_hap_entry(h) for h in branch_rel["yuk_hap"]]

    # 십성 분포: 0 제거 후 퍼센트 변환 (총합 100%)
    _dist_nonzero = {k: v for k, v in ten_gods_dist.items() if v > 0}
    _total = sum(_dist_nonzero.values())
    ten_gods_dist_filtered = (
        {k: round(v / _total * 100, 1) for k, v in _dist_nonzero.items()}
        if _total > 0 else {}
    )
    # 결핍 카테고리 → void_info: 표면(0) + 지장간 잠재력 대조
    _CATEGORIES = {
        "비겁": ["비견", "겁재"], "식상": ["식신", "상관"],
        "재성": ["편재", "정재"], "관성": ["편관", "정관"], "인성": ["편인", "정인"],
    }
    _ji_pillar_keys = ["year", "month", "day", "hour"]
    ten_gods_void_info = []
    for cat, gods in _CATEGORIES.items():
        if all(ten_gods_dist_filtered.get(g, 0) == 0 for g in gods):
            hidden: dict[str, list[str]] = {}
            for pk in _ji_pillar_keys:
                stems = [s for s in saju["ji_jang_gan"][pk]
                         if calculate_ten_god(day_stem, s) in gods]
                if stems:
                    hidden[pk] = stems
            ten_gods_void_info.append({"category": cat, "hidden_in_ji_jang_gan": hidden})

    # 오행 분포 퍼센트 변환 (총합 8글자 기준, 0도 포함 — 결핍 오행도 의미 있음)
    _wuxing_total = sum(saju["wuxing_count"].values())
    wuxing_pct = (
        {k: round(v / _wuxing_total * 100, 1) for k, v in saju["wuxing_count"].items()}
        if _wuxing_total > 0 else saju["wuxing_count"]
    )

    # 조후(調候) — 월지 기후와 일간의 관계
    _SEASON_MAP: dict[str, tuple] = {
        "인": ("spring", "warm",      "humid"),
        "묘": ("spring", "warm",      "humid"),
        "진": ("spring", "warm",      "moderate"),
        "사": ("summer", "hot",       "dry"),
        "오": ("summer", "scorching", "dry"),
        "미": ("summer", "hot",       "moderate"),
        "신": ("autumn", "cool",      "dry"),
        "유": ("autumn", "cool",      "dry"),
        "술": ("autumn", "cool",      "moderate"),
        "해": ("winter", "cold",      "wet"),
        "자": ("winter", "cold",      "wet"),
        "축": ("winter", "cold",      "dry"),
    }
    month_branch = saju["month_pillar"]["branch"]
    month_el = saju["month_pillar"]["branch_element"]
    day_el   = saju["day_pillar"]["stem_element"]
    season, temperature, humidity = _SEASON_MAP.get(month_branch, ("unknown", "moderate", "moderate"))
    if WUXING_GENERATION.get(month_el) == day_el:
        _season_relation = "생(生)"    # 계절이 일간을 생함
    elif WUXING_GENERATION.get(day_el) == month_el:
        _season_relation = "설(洩)"    # 일간이 계절을 설기
    elif WUXING_DESTRUCTION.get(month_el) == day_el:
        _season_relation = "극(剋)"    # 계절이 일간을 극
    elif WUXING_DESTRUCTION.get(day_el) == month_el:
        _season_relation = "재(財)"    # 일간이 계절을 극
    else:
        _season_relation = "비(比)"    # 동기
    climate_vibe = {
        "season": season, "temperature": temperature, "humidity": humidity,
        "month_element": month_el, "day_element_relation": _season_relation,
    }

    # 반복 연산 방지: 결과를 로컬 변수에 캐싱
    _structure_patterns = detect_structure_patterns(ten_gods_dist_filtered, strength["level"], wuxing_pct)
    _dynamics = build_dynamics(saju, branch_rel, wuxing_pct)
    _synergy = compute_synergy_tags(_structure_patterns, _dynamics)

    # ⑩ 행동 프로파일 — 십성 분포 → 원자적 행동 벡터 합성
    _behavior_profile = synthesize_behavior_profile(ten_gods_dist_filtered)

    # ⑪ 컨텍스트 랭킹 — Writer에게 전달할 핵심·보조 컨텍스트 선별
    _context_ranking = rank_context(_structure_patterns, sin_sals, synergy=_synergy)

    # ⑫ 생활 도메인 매핑 — 연애·직업·돈·성격별 핵심 태그 자동 분류
    _life_domains = map_life_domains(_behavior_profile, _context_ranking)

    return {
        # ① meta — 계산 기준 먼저
        "meta": {
            **meta,
            "gender": saju["gender"],
            "birth_date": saju["birth_date"],
            "birth_time": saju["birth_time"],
            "calendar": saju["calendar"],
            "climate_vibe": climate_vibe,
        },
        # ② 핵심 결론
        "day_master_strength": strength,
        "yong_sin": yong_sin,
        "gyeok_guk": gyeok_guk,
        # ③ 4기둥 (십성·12운성 포함)
        "year_pillar": pillars_enriched["year_pillar"],
        "month_pillar": pillars_enriched["month_pillar"],
        "day_pillar": pillars_enriched["day_pillar"],
        "hour_pillar": pillars_enriched["hour_pillar"],
        # ④ 오행·음양 분포 (퍼센트, 0 포함 — 결핍 오행도 의미 있음)
        "wuxing_count": wuxing_pct,
        "dominant_elements": saju["dominant_elements"],
        "weak_elements": saju["weak_elements"],
        "yin_yang_ratio": yin_yang_ratio,
        # ⑤ 십성 분포 % (총합 ~100) + 결핍 카테고리 (표면 없음 + 지장간 잠재력 대조)
        "ten_gods_distribution": ten_gods_dist_filtered,
        "ten_gods_void_info": ten_gods_void_info,
        "structure_patterns": _structure_patterns,
        # ⑥ 특이사항
        "sin_sals": sin_sals,
        "branch_relations": branch_rel,
        "ji_jang_gan": saju["ji_jang_gan"],
        # ⑦ 대운 (전체 리스트 + 현재 대운)
        "dae_un_start_age": dae_un_list[0]["start_age"],
        "dae_un_list": dae_un_list,
        "current_dae_un": current_dae_un,
        # ⑧ 동역학 — 기둥 간 상호작용 (천간합·통근·지지관계위치·오행흐름)
        "dynamics": _dynamics,
        # ⑨ 시너지 — 구조 패턴 × 동역학 교차점 (Writer Agent 추가 해석 힌트)
        "synergy": _synergy,
        # ⑩ 행동 프로파일 — 십성 → 원자적 행동 벡터 (RAG 쿼리 seed)
        "behavior_profile": _behavior_profile,
        # ⑪ 컨텍스트 랭킹 — Writer 전달 핵심·보조 컨텍스트 (primary 3 + secondary 2)
        "context_ranking": _context_ranking,
        # ⑫ 생활 도메인 — 연애·직업·돈·성격 도메인별 핵심 태그 (Planner Agent RAG 쿼리 seed)
        "life_domains": _life_domains,
    }
