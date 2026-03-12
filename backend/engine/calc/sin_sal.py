"""
신살(神殺) 판단 — 10종.
Strategy + Registry 패턴: 각 신살을 체커 함수로 등록하고 순회 평가.
"""

from __future__ import annotations
from datetime import datetime
from typing import Callable
from engine.data.earthly_branches import GONG_MANG_TABLE

# ─── 정적 데이터 ────────────────────────────────────────────────

_CHEON_EUL_TABLE: dict[str, list[str]] = {
    "갑": ["축", "미"], "을": ["자", "신"],
    "병": ["해", "유"], "정": ["해", "유"],
    "무": ["축", "미"], "기": ["자", "신"],
    "경": ["축", "미"], "신": ["인", "오"],
    "임": ["사", "묘"], "계": ["사", "묘"],
}

_DO_HWA_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "묘"), ({"사", "유", "축"}, "오"),
    ({"신", "자", "진"}, "유"), ({"해", "묘", "미"}, "자"),
]

_YEOK_MA_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "신"), ({"사", "유", "축"}, "해"),
    ({"신", "자", "진"}, "인"), ({"해", "묘", "미"}, "사"),
]

_HWA_GAE_GROUPS: list[tuple[set[str], str]] = [
    ({"인", "오", "술"}, "술"), ({"사", "유", "축"}, "축"),
    ({"신", "자", "진"}, "진"), ({"해", "묘", "미"}, "미"),
]


_GWI_MUN_BRANCHES: set[str] = {"인", "신", "사", "해"}

_YANG_IN_TABLE: dict[str, str] = {
    "갑": "묘", "병": "오", "무": "오", "경": "유", "임": "자",
    "을": "진", "정": "미", "기": "미", "신": "술", "계": "축",
}

_BAEK_HO_PAIRS: set[tuple[str, str]] = {
    ("갑", "진"), ("을", "미"), ("병", "술"), ("정", "축"),
    ("무", "진"), ("기", "미"), ("경", "술"), ("신", "축"),
    ("임", "진"), ("계", "미"),
}

# ── 추가 8종 정적 데이터 ─────────────────────────────────────────

_HYEON_CHIM_STEMS: set[str] = {"갑", "신", "임"}
_HYEON_CHIM_BRANCHES: set[str] = {"오", "묘", "신"}

_TAE_GEUK_TABLE: dict[str, list[str]] = {
    "갑": ["자", "오"], "을": ["자", "오"],
    "병": ["묘", "유"], "정": ["묘", "유"],
    "무": ["진", "술", "축", "미"], "기": ["진", "술", "축", "미"],
    "경": ["인", "오"], "신": ["인", "오"],
    "임": ["사", "신"], "계": ["사", "신"],
}

_MUN_GOK_TABLE: dict[str, str] = {
    "갑": "해", "을": "자", "병": "인", "정": "묘",
    "무": "진", "기": "사", "경": "오", "신": "미",
    "임": "신", "계": "유",
}

_GWAN_GWI_TABLE: dict[str, str] = {
    "갑": "해", "을": "오", "병": "인", "정": "유",
    "무": "인", "기": "유", "경": "사", "신": "자",
    "임": "신", "계": "묘",
}

_HONG_YEOM_TABLE: dict[str, str] = {
    "갑": "오", "을": "오", "병": "인", "정": "미",
    "무": "진", "기": "진", "경": "술", "신": "유",
    "임": "자", "계": "신",
}

_GO_SIN_TABLE: dict[str, str] = {
    "자": "인", "축": "인", "인": "사",
    "묘": "사", "진": "사", "사": "신",
    "오": "신", "미": "신", "신": "해",
    "유": "해", "술": "해", "해": "인",
}

_WOL_DEOK_TABLE: dict[str, str] = {
    "인": "병", "오": "병", "술": "병",
    "사": "경", "유": "경", "축": "경",
    "신": "임", "자": "임", "진": "임",
    "해": "갑", "묘": "갑", "미": "갑",
}

_HWANG_EUN_PILLARS: set[tuple[str, str]] = {
    ("갑", "자"), ("갑", "술"), ("갑", "진"),
    ("을", "해"), ("을", "묘"),
    ("병", "자"), ("병", "오"), ("병", "인"),
    ("정", "묘"),
    ("무", "자"), ("무", "오"),
    ("기", "사"), ("기", "해"),
    ("경", "자"), ("경", "오"), ("경", "신"),
    ("신", "유"),
    ("임", "자"), ("임", "신"),
    ("계", "사"), ("계", "해"),
}

_SAM_JAE_TABLE: list[tuple[frozenset[str], list[str]]] = [
    (frozenset({"인", "오", "술"}), ["해", "자", "축"]),
    (frozenset({"사", "유", "축"}), ["인", "묘", "진"]),
    (frozenset({"신", "자", "진"}), ["사", "오", "미"]),
    (frozenset({"해", "묘", "미"}), ["신", "유", "술"]),
]

_BRANCH_ORDER = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

SIN_SAL_INFO: dict[str, dict] = {
    "천을귀인": {"name": "천을귀인", "type": "lucky",   "desc": "인복이 많고 위기에서 귀인의 도움을 받음"},
    "도화살":   {"name": "도화살",   "type": "neutral", "desc": "매력과 끼가 넘치며 이성에게 인기가 많음"},
    "역마살":   {"name": "역마살",   "type": "neutral", "desc": "활동적이고 변화를 즐기며 해외·이동 인연이 있음"},
    "화개살":   {"name": "화개살",   "type": "neutral", "desc": "예술·종교적 감수성이 뛰어나고 고독함을 즐김"},
    "공망":     {"name": "공망",     "type": "unlucky", "desc": "해당 지지의 기운이 허(虛)하여 그 분야가 약해짐"},
    "원진살":   {"name": "원진살",   "type": "unlucky", "desc": "서로 싫어하고 미워하는 관계 인연이 많음"},
    "귀문관살": {"name": "귀문관살", "type": "unlucky", "desc": "예민한 직관력과 창의적 영감, 신경과민 주의"},
    "양인살":   {"name": "양인살",   "type": "unlucky", "desc": "강한 추진력과 승부욕, 다혈질적 기질"},
    "백호대살": {"name": "백호대살", "type": "unlucky", "desc": "급작스러운 사고·변화, 강한 기운의 양날의 검"},
    # ── 추가 8종 ─────────────────────────────────────────────────
    "현침살":   {"name": "현침살",   "type": "neutral", "desc": "날카로운 직관과 비판력, 언변·문장에 재주가 있음"},
    "태극귀인": {"name": "태극귀인", "type": "lucky",   "desc": "역경에서 회복력이 강하고 반전의 기운이 있음"},
    "문곡귀인": {"name": "문곡귀인", "type": "lucky",   "desc": "학문과 문서 운이 좋고 글재주가 뛰어남"},
    "관귀학관": {"name": "관귀학관", "type": "lucky",   "desc": "학문·관직 운이 강하고 시험·승진에 유리함"},
    "홍염살":   {"name": "홍염살",   "type": "neutral", "desc": "이성에게 매력적이고 예술·연예 감각이 풍부함"},
    "고신살":   {"name": "고신살",   "type": "unlucky", "desc": "고독하고 독립적인 기질, 혼자 있는 시간이 많음"},
    "월덕귀인": {"name": "월덕귀인", "type": "lucky",   "desc": "공적 업무·관공서 운이 좋고 사회적 덕망이 있음"},
    "황은대사": {"name": "황은대사", "type": "lucky",   "desc": "귀한 은혜를 받고 특별한 인연이나 기회가 찾아옴"},
}


# ─── 체커 함수 ──────────────────────────────────────────────────
# 각 체커: (saju, branch_set) → dict | None

def _find_group(
    branch_set: set[str], groups: list[tuple[set[str], str]]
) -> tuple[set[str], str] | None:
    """삼합 그룹 중 조건 충족하는 첫 번째 항목 반환."""
    for group, sal in groups:
        if group & branch_set and sal in branch_set:
            return group, sal
    return None


SinSalChecker = Callable[[dict, set[str]], dict | None]

# ── 체커 팩토리 (Factory Pattern) ────────────────────────────────────

def _make_stem_multi(name: str, table: dict[str, list[str]]) -> "SinSalChecker":
    """일간 → 복수 지지 조회 체커 (천을귀인·태극귀인)."""
    def checker(saju: dict, bs: set[str]) -> dict | None:
        stem = saju["day_pillar"]["stem"]
        matched = [b for b in table.get(stem, []) if b in bs]
        if not matched:
            return None
        r = dict(SIN_SAL_INFO[name])
        r["reason"] = {"trigger": "day_stem", "day_stem": stem, "matched_branches": matched}
        r["_location_branches"] = matched
        return r
    return checker


def _make_stem_single(name: str, table: dict[str, str]) -> "SinSalChecker":
    """일간 → 단일 지지 조회 체커 (문곡귀인·관귀학관·홍염살)."""
    def checker(saju: dict, bs: set[str]) -> dict | None:
        stem = saju["day_pillar"]["stem"]
        target = table.get(stem)
        if not target or target not in bs:
            return None
        r = dict(SIN_SAL_INFO[name])
        r["reason"] = {"trigger": "day_stem", "day_stem": stem, "target_branch": target}
        r["_location_branches"] = [target]
        return r
    return checker


def _make_group_branch(name: str, groups: list[tuple[set[str], str]], label_key: str) -> "SinSalChecker":
    """삼합 그룹 체커 (도화살·역마살·화개살)."""
    def checker(_saju: dict, bs: set[str]) -> dict | None:
        m = _find_group(bs, groups)
        if m is None:
            return None
        group, sal = m
        group_matched = sorted(group & bs, key=lambda x: _BRANCH_ORDER.index(x))
        r = dict(SIN_SAL_INFO[name])
        r["reason"] = {"trigger": "branch_group", "group_branches": group_matched, label_key: sal}
        r["_location_branches"] = group_matched + [sal]
        return r
    return checker


_cheon_eul = _make_stem_multi("천을귀인", _CHEON_EUL_TABLE)
_do_hwa    = _make_group_branch("도화살", _DO_HWA_GROUPS, "도화지")
_yeok_ma   = _make_group_branch("역마살", _YEOK_MA_GROUPS, "역마지")
_hwa_gae   = _make_group_branch("화개살", _HWA_GAE_GROUPS, "화개지")

def _gong_mang(saju: dict, bs: set[str]) -> dict | None:
    day_branch = saju["day_pillar"]["branch"]
    gong_branches = GONG_MANG_TABLE.get(day_branch, [])
    matched = [b for b in gong_branches if b in bs]
    if not matched:
        return None
    r = dict(SIN_SAL_INFO["공망"])
    r["reason"] = {"trigger": "day_branch", "day_branch": day_branch, "gong_branches": gong_branches, "matched_branches": matched}
    r["_location_branches"] = matched
    return r

_WON_JIN_PAIRS: list[tuple[str, str]] = [
    ("자", "미"), ("축", "오"), ("인", "유"),
    ("묘", "신"), ("진", "해"), ("사", "술"),
]

def _won_jin(_saju: dict, bs: set[str]) -> dict | None:
    for a, b in _WON_JIN_PAIRS:
        if a in bs and b in bs:
            r = dict(SIN_SAL_INFO["원진살"])
            r["reason"] = {"trigger": "branch_pair", "pair": [a, b]}
            r["_location_branches"] = [a, b]
            return r
    return None

def _gwi_mun(_saju: dict, bs: set[str]) -> dict | None:
    found = _GWI_MUN_BRANCHES & bs
    if len(found) < 2:
        return None
    matched = sorted(found, key=lambda x: _BRANCH_ORDER.index(x))
    r = dict(SIN_SAL_INFO["귀문관살"])
    r["reason"] = {"trigger": "branch_count", "matched_branches": matched, "required_count": 2}
    r["_location_branches"] = matched
    return r

def _yang_in(saju: dict, bs: set[str]) -> dict | None:
    stem = saju["day_pillar"]["stem"]
    yang_in = _YANG_IN_TABLE.get(stem)
    if not yang_in or yang_in not in bs:
        return None
    r = dict(SIN_SAL_INFO["양인살"])
    r["reason"] = {"trigger": "day_stem", "day_stem": stem, "yang_in_branch": yang_in}
    r["_location_branches"] = [yang_in]
    return r

def _baek_ho(saju: dict, _bs: set[str]) -> dict | None:
    p = saju["day_pillar"]
    if (p["stem"], p["branch"]) not in _BAEK_HO_PAIRS:
        return None
    r = dict(SIN_SAL_INFO["백호대살"])
    r["reason"] = {"trigger": "day_pillar", "day_stem": p["stem"], "day_branch": p["branch"]}
    r["_location_branches"] = [p["branch"]]
    return r

def _sam_jae(saju: dict, _bs: set[str]) -> dict | None:
    year_branch = saju["year_pillar"]["branch"]
    current_branch = _BRANCH_ORDER[(datetime.now().year - 4) % 12]
    for group, branches in _SAM_JAE_TABLE:
        if year_branch in group and current_branch in branches:
            idx = branches.index(current_branch)
            status = ["들삼재", "묵삼재", "날삼재"][idx]
            return {
                "name": "삼재", "type": "warning",
                "desc": "3년 주기 액운 구간",
                "status": status,
                "reason": {"trigger": "year_branch_cycle", "birth_year_branch": year_branch, "current_year_branch": current_branch, "status": status},
                "_location_branches": [year_branch],
            }
    return None


def _hyeon_chim(saju: dict, _bs: set[str]) -> dict | None:
    trigger_pillars = []
    for short, key in zip(_PILLAR_ORDER, ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]):
        if saju.get(key) is None:
            continue
        if saju[key]["stem"] in _HYEON_CHIM_STEMS or saju[key]["branch"] in _HYEON_CHIM_BRANCHES:
            trigger_pillars.append(short)
    if not trigger_pillars:
        return None
    r = dict(SIN_SAL_INFO["현침살"])
    r["reason"] = {"trigger": "stem_or_branch",
                   "stems": list(_HYEON_CHIM_STEMS), "branches": list(_HYEON_CHIM_BRANCHES)}
    r["_location_pillars"] = trigger_pillars
    r["_location_branches"] = []
    return r


_tae_geuk  = _make_stem_multi("태극귀인", _TAE_GEUK_TABLE)
_mun_gok   = _make_stem_single("문곡귀인", _MUN_GOK_TABLE)
_gwan_gwi  = _make_stem_single("관귀학관", _GWAN_GWI_TABLE)
_hong_yeom = _make_stem_single("홍염살", _HONG_YEOM_TABLE)


def _go_sin(saju: dict, bs: set[str]) -> dict | None:
    year_branch = saju["year_pillar"]["branch"]
    target = _GO_SIN_TABLE.get(year_branch)
    if not target or target not in bs:
        return None
    r = dict(SIN_SAL_INFO["고신살"])
    r["reason"] = {"trigger": "year_branch", "year_branch": year_branch, "target_branch": target}
    r["_location_branches"] = [target]
    return r


def _wol_deok(saju: dict, _bs: set[str]) -> dict | None:
    month_branch = saju["month_pillar"]["branch"]
    deok_stem = _WOL_DEOK_TABLE.get(month_branch)
    if not deok_stem or saju["day_pillar"]["stem"] != deok_stem:
        return None
    r = dict(SIN_SAL_INFO["월덕귀인"])
    r["reason"] = {"trigger": "month_branch_day_stem",
                   "month_branch": month_branch, "deok_stem": deok_stem}
    r["_location_pillars"] = ["day"]
    r["_location_branches"] = []
    return r


def _hwang_eun(saju: dict, _bs: set[str]) -> dict | None:
    day = saju["day_pillar"]
    if (day["stem"], day["branch"]) not in _HWANG_EUN_PILLARS:
        return None
    r = dict(SIN_SAL_INFO["황은대사"])
    r["reason"] = {"trigger": "day_pillar",
                   "day_stem": day["stem"], "day_branch": day["branch"]}
    r["_location_pillars"] = ["day"]
    r["_location_branches"] = []
    return r


# ─── 레지스트리 ─────────────────────────────────────────────────

_CHECKERS: list[SinSalChecker] = [
    _cheon_eul, _do_hwa, _yeok_ma, _hwa_gae,
    _gong_mang, _won_jin, _gwi_mun,
    _yang_in, _baek_ho, _sam_jae,
    # 추가 8종
    _hyeon_chim, _tae_geuk, _mun_gok, _gwan_gwi,
    _hong_yeom, _go_sin, _wol_deok, _hwang_eun,
]


# ─── 공개 API ───────────────────────────────────────────────────

_PILLAR_ORDER = ["year", "month", "day", "hour"]

def find_sin_sals(saju: dict) -> list[dict]:
    """사주에서 해당하는 신살 목록 반환 [{name, type, desc, location, reason, ...}]."""
    _active_keys = [k for k in ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]
                    if saju.get(k) is not None]
    branch_set = {saju[k]["branch"] for k in _active_keys}

    # 지지 → 기둥 위치 매핑 (중복 지지 허용)
    branch_to_pillars: dict[str, list[str]] = {}
    for short, key in zip(_PILLAR_ORDER, ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]):
        if saju.get(key) is None:
            continue
        b = saju[key]["branch"]
        branch_to_pillars.setdefault(b, []).append(short)

    results = []
    for checker in _CHECKERS:
        r = checker(saju, branch_set)
        if r is None:
            continue
        # 각 체커가 직접 선언한 _location_branches로 위치 계산
        trigger_branches = r.pop("_location_branches", [])
        trigger_pillars  = r.pop("_location_pillars", [])
        branch_pillars = {p for b in trigger_branches for p in branch_to_pillars.get(b, [])}
        r["location"] = sorted(
            branch_pillars | set(trigger_pillars),
            key=lambda x: _PILLAR_ORDER.index(x),
        )
        results.append(r)
    return results


# ─── 12신살 (기둥별) ─────────────────────────────────────────────

_TWELVE_SIN_SAL_GROUPS: dict[str, dict[str, str]] = {
    "인오술": {
        "해": "겁살", "자": "재살", "축": "천살", "인": "지살",
        "묘": "년살", "진": "월살", "사": "망신살", "오": "장성살",
        "미": "반안살", "신": "역마살", "유": "육해살", "술": "화개살",
    },
    "사유축": {
        "인": "겁살", "묘": "재살", "진": "천살", "사": "지살",
        "오": "년살", "미": "월살", "신": "망신살", "유": "장성살",
        "술": "반안살", "해": "역마살", "자": "육해살", "축": "화개살",
    },
    "신자진": {
        "사": "겁살", "오": "재살", "미": "천살", "신": "지살",
        "유": "년살", "술": "월살", "해": "망신살", "자": "장성살",
        "축": "반안살", "인": "역마살", "묘": "육해살", "진": "화개살",
    },
    "해묘미": {
        "신": "겁살", "유": "재살", "술": "천살", "해": "지살",
        "자": "년살", "축": "월살", "인": "망신살", "묘": "장성살",
        "진": "반안살", "사": "역마살", "오": "육해살", "미": "화개살",
    },
}

_YEAR_BRANCH_TO_GROUP: dict[str, str] = {
    "인": "인오술", "오": "인오술", "술": "인오술",
    "사": "사유축", "유": "사유축", "축": "사유축",
    "신": "신자진", "자": "신자진", "진": "신자진",
    "해": "해묘미", "묘": "해묘미", "미": "해묘미",
}


def find_twelve_sin_sals_per_pillar(saju: dict) -> dict[str, str]:
    """연지(年支) 기준 삼합국으로 각 기둥의 12신살 이름 반환.

    Returns:
        {"year": "지살", "month": "망신살", "day": "육해살", "hour": "지살"}
    """
    year_branch = saju["year_pillar"]["branch"]
    group_key = _YEAR_BRANCH_TO_GROUP.get(year_branch)
    if not group_key:
        return {}
    group = _TWELVE_SIN_SAL_GROUPS[group_key]
    return {
        short: group.get(saju[key]["branch"], "")
        for short, key in zip(
            _PILLAR_ORDER,
            ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"],
        )
        if saju.get(key) is not None
    }
