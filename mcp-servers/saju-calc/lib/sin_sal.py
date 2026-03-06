"""
신살(神殺) 판단 — 10종.
Strategy + Registry 패턴: 각 신살을 체커 함수로 등록하고 순회 평가.
"""

from __future__ import annotations
from datetime import datetime
from typing import Callable
from data.earthly_branches import GONG_MANG_TABLE

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

_CHUNG_PAIRS: list[tuple[str, str]] = [
    ("자", "오"), ("축", "미"), ("인", "신"),
    ("묘", "유"), ("진", "술"), ("사", "해"),
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
}


# ─── 체커 함수 ──────────────────────────────────────────────────
# 각 체커: (saju, branch_set) → dict | None

def _check_group(branch_set: set[str], groups: list[tuple[set[str], str]]) -> bool:
    return any(group & branch_set and sal in branch_set for group, sal in groups)


SinSalChecker = Callable[[dict, set[str]], dict | None]

def _cheon_eul(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["천을귀인"]) if any(
        b in bs for b in _CHEON_EUL_TABLE.get(saju["day_pillar"]["stem"], [])
    ) else None

def _do_hwa(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["도화살"]) if _check_group(bs, _DO_HWA_GROUPS) else None

def _yeok_ma(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["역마살"]) if _check_group(bs, _YEOK_MA_GROUPS) else None

def _hwa_gae(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["화개살"]) if _check_group(bs, _HWA_GAE_GROUPS) else None

def _gong_mang(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["공망"]) if any(
        b in bs for b in GONG_MANG_TABLE.get(saju["day_pillar"]["branch"], [])
    ) else None

def _won_jin(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["원진살"]) if any(
        a in bs and b in bs for a, b in _CHUNG_PAIRS
    ) else None

def _gwi_mun(saju: dict, bs: set[str]) -> dict | None:
    return dict(SIN_SAL_INFO["귀문관살"]) if len(_GWI_MUN_BRANCHES & bs) >= 2 else None

def _yang_in(saju: dict, bs: set[str]) -> dict | None:
    yang_in = _YANG_IN_TABLE.get(saju["day_pillar"]["stem"])
    return dict(SIN_SAL_INFO["양인살"]) if yang_in and yang_in in bs else None

def _baek_ho(saju: dict, bs: set[str]) -> dict | None:
    p = saju["day_pillar"]
    return dict(SIN_SAL_INFO["백호대살"]) if (p["stem"], p["branch"]) in _BAEK_HO_PAIRS else None

def _sam_jae(saju: dict, bs: set[str]) -> dict | None:
    year_branch = saju["year_pillar"]["branch"]
    current_branch = _BRANCH_ORDER[(datetime.now().year - 4) % 12]
    for group, branches in _SAM_JAE_TABLE:
        if year_branch in group and current_branch in branches:
            idx = branches.index(current_branch)
            return {
                "name": "삼재", "type": "warning",
                "desc": "3년 주기 액운 구간",
                "status": ["들삼재", "묵삼재", "날삼재"][idx],
            }
    return None


# ─── 레지스트리 ─────────────────────────────────────────────────

_CHECKERS: list[SinSalChecker] = [
    _cheon_eul, _do_hwa, _yeok_ma, _hwa_gae,
    _gong_mang, _won_jin, _gwi_mun,
    _yang_in, _baek_ho, _sam_jae,
]


# ─── 공개 API ───────────────────────────────────────────────────

def find_sin_sals(saju: dict) -> list[dict]:
    """사주에서 해당하는 신살 목록 반환 [{name, type, desc, ...}]."""
    branch_set = {saju[k]["branch"] for k in
                  ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"]}
    return [r for checker in _CHECKERS if (r := checker(saju, branch_set)) is not None]
