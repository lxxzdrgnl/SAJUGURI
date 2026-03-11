"""
지지(地支) 정적 데이터
자·축·인·묘·진·사·오·미·신·유·술·해 — 12개
+ 지장간(支藏干), 삼합(三合), 삼형(三刑), 육해(六害), 충(沖), 육합(六合)
"""

EARTHLY_BRANCHES: list[dict] = [
    {"korean": "자", "hanja": "子", "element": "수", "yin_yang": "양", "animal": "쥐",  "month": 11, "direction": "북",   "index": 0},
    {"korean": "축", "hanja": "丑", "element": "토", "yin_yang": "음", "animal": "소",  "month": 12, "direction": "북북동", "index": 1},
    {"korean": "인", "hanja": "寅", "element": "목", "yin_yang": "양", "animal": "호랑이", "month": 1, "direction": "동북동", "index": 2},
    {"korean": "묘", "hanja": "卯", "element": "목", "yin_yang": "음", "animal": "토끼", "month": 2, "direction": "동",   "index": 3},
    {"korean": "진", "hanja": "辰", "element": "토", "yin_yang": "양", "animal": "용",  "month": 3, "direction": "동남동", "index": 4},
    {"korean": "사", "hanja": "巳", "element": "화", "yin_yang": "음", "animal": "뱀",  "month": 4, "direction": "남남동", "index": 5},
    {"korean": "오", "hanja": "午", "element": "화", "yin_yang": "양", "animal": "말",  "month": 5, "direction": "남",   "index": 6},
    {"korean": "미", "hanja": "未", "element": "토", "yin_yang": "음", "animal": "양",  "month": 6, "direction": "남남서", "index": 7},
    {"korean": "신", "hanja": "申", "element": "금", "yin_yang": "양", "animal": "원숭이", "month": 7, "direction": "서남서", "index": 8},
    {"korean": "유", "hanja": "酉", "element": "금", "yin_yang": "음", "animal": "닭",  "month": 8, "direction": "서",   "index": 9},
    {"korean": "술", "hanja": "戌", "element": "토", "yin_yang": "양", "animal": "개",  "month": 9, "direction": "서북서", "index": 10},
    {"korean": "해", "hanja": "亥", "element": "수", "yin_yang": "음", "animal": "돼지", "month": 10, "direction": "북북서", "index": 11},
]

# O(1) 조회용 dict
BRANCHES_BY_INDEX: dict[int, dict] = {b["index"]: b for b in EARTHLY_BRANCHES}
BRANCHES_BY_KOREAN: dict[str, dict] = {b["korean"]: b for b in EARTHLY_BRANCHES}

# 순서 리스트 (인덱스 계산용)
BRANCHES_ORDER: list[str] = [b["korean"] for b in EARTHLY_BRANCHES]

# ──────────────────────────────────────────
# 지장간(支藏干) — 지지 안에 숨은 천간
# primary: 정기(正氣), secondary: 중기(中氣), residual: 여기(餘氣)
# ──────────────────────────────────────────
JI_JANG_GAN: dict[str, dict] = {
    "자": {"primary": "계"},
    "축": {"primary": "기",  "secondary": "신", "residual": "계"},
    "인": {"primary": "갑",  "secondary": "병", "residual": "무"},
    "묘": {"primary": "을"},
    "진": {"primary": "무",  "secondary": "을", "residual": "계"},
    "사": {"primary": "병",  "secondary": "무", "residual": "경"},
    "오": {"primary": "정",  "secondary": "기"},
    "미": {"primary": "기",  "secondary": "정", "residual": "을"},
    "신": {"primary": "경",  "secondary": "임", "residual": "무"},
    "유": {"primary": "신"},
    "술": {"primary": "무",  "secondary": "신", "residual": "정"},
    "해": {"primary": "임",  "secondary": "갑"},
}

# ──────────────────────────────────────────
# 삼합(三合) — 3지지가 모이면 해당 오행으로 화국
# ──────────────────────────────────────────
SAM_HAP: dict[str, dict] = {
    "수국": {"branches": ["신", "자", "진"], "element": "수", "name": "신자진 수국"},
    "목국": {"branches": ["해", "묘", "미"], "element": "목", "name": "해묘미 목국"},
    "화국": {"branches": ["인", "오", "술"], "element": "화", "name": "인오술 화국"},
    "금국": {"branches": ["사", "유", "축"], "element": "금", "name": "사유축 금국"},
}

# ──────────────────────────────────────────
# 육합(六合) — 2지지가 합하여 오행 변화
# ──────────────────────────────────────────
YUK_HAP: list[dict] = [
    {"pair": ("자", "축"), "element": "토"},
    {"pair": ("인", "해"), "element": "목"},
    {"pair": ("묘", "술"), "element": "화"},
    {"pair": ("진", "유"), "element": "금"},
    {"pair": ("사", "신"), "element": "수"},
    {"pair": ("오", "미"), "element": "토"},
]

# ──────────────────────────────────────────
# 충(沖) — 서로 마주보며 충돌하는 쌍 (6쌍)
# ──────────────────────────────────────────
CHUNG_PAIRS: list[tuple] = [
    ("자", "오"),
    ("축", "미"),
    ("인", "신"),
    ("묘", "유"),
    ("진", "술"),
    ("사", "해"),
]

# ──────────────────────────────────────────
# 삼형(三刑) — 형벌 관계
# ──────────────────────────────────────────
SAM_HYEONG: dict[str, list] = {
    "무은지형": ["인", "사", "신"],   # 은의를 모르는 형
    "지세지형": ["축", "술", "미"],   # 세력을 믿는 형
    "무례지형": ["자", "묘"],          # 무례한 형
    "자형_진":  ["진", "진"],          # 자기 자신을 형
    "자형_오":  ["오", "오"],
    "자형_유":  ["유", "유"],
    "자형_해":  ["해", "해"],
}

# ──────────────────────────────────────────
# 육해(六害) — 서로 방해하는 쌍
# ──────────────────────────────────────────
YUK_HAE: list[tuple] = [
    ("자", "미"),
    ("축", "오"),
    ("인", "사"),
    ("묘", "진"),
    ("신", "해"),
    ("유", "술"),
]

# ──────────────────────────────────────────
# 공망(空亡) — 일주 기준 빈 지지 쌍
# ──────────────────────────────────────────
GONG_MANG_TABLE: dict[str, list] = {
    "자": ["술", "해"],
    "축": ["술", "해"],
    "인": ["자", "축"],
    "묘": ["자", "축"],
    "진": ["인", "묘"],
    "사": ["인", "묘"],
    "오": ["진", "사"],
    "미": ["진", "사"],
    "신": ["오", "미"],
    "유": ["오", "미"],
    "술": ["신", "유"],
    "해": ["신", "유"],
}


def get_branch_by_index(index: int) -> dict:
    """인덱스로 지지 조회 (음수·범위 초과 자동 보정)"""
    return BRANCHES_BY_INDEX[index % 12]


def get_branch_by_korean(korean: str) -> dict:
    return BRANCHES_BY_KOREAN[korean]


def get_ji_jang_gan(branch: str) -> list[str]:
    """지지에서 지장간 천간 목록 반환 (정기→중기→여기 순)"""
    jjg = JI_JANG_GAN[branch]
    result = [jjg["primary"]]
    if "secondary" in jjg:
        result.append(jjg["secondary"])
    if "residual" in jjg:
        result.append(jjg["residual"])
    return result


def check_sam_hap(branches: list[str]) -> dict | None:
    """삼합 확인. 3개 모두 있으면 화국 정보 반환, 없으면 None"""
    branch_set = set(branches)
    for name, data in SAM_HAP.items():
        if all(b in branch_set for b in data["branches"]):
            return {"name": name, "element": data["element"], "label": data["name"], "branches": data["branches"]}
    return None


def check_yuk_hap(branches: list[str]) -> list[dict]:
    """육합 확인. 합이 되는 쌍과 합화 오행 목록 반환"""
    branch_set = set(branches)
    result = []
    for item in YUK_HAP:
        a, b = item["pair"]
        if a in branch_set and b in branch_set:
            result.append({"pair": (a, b), "element": item["element"]})
    return result


def check_chung(branches: list[str]) -> list[tuple]:
    """충 확인. 충 관계인 쌍 목록 반환"""
    branch_set = set(branches)
    return [pair for pair in CHUNG_PAIRS if pair[0] in branch_set and pair[1] in branch_set]


def check_sam_hyeong(branches: list[str]) -> list[str]:
    """삼형 확인. 해당되는 형 이름 목록 반환"""
    branch_set = set(branches)
    result = []
    for name, members in SAM_HYEONG.items():
        if name.startswith("자형"):
            if branches.count(members[0]) >= 2:
                result.append(name)
        elif all(m in branch_set for m in members):
            result.append(name)
    return result


def check_yuk_hae(branches: list[str]) -> list[tuple]:
    """육해 확인. 해 관계인 쌍 목록 반환"""
    branch_set = set(branches)
    return [pair for pair in YUK_HAE if pair[0] in branch_set and pair[1] in branch_set]


def check_gong_mang(day_branch: str, branches: list[str]) -> list[str]:
    """공망 확인. 일주 기준 공망인 지지 목록 반환"""
    gong_mang = GONG_MANG_TABLE[day_branch]
    return [b for b in branches if b in gong_mang]


def analyze_branch_relations(branches: list[str], day_branch: str) -> dict:
    """4기둥 지지 전체 관계 종합 분석"""
    return {
        "sam_hap":   check_sam_hap(branches),
        "yuk_hap":   check_yuk_hap(branches),
        "chung":     check_chung(branches),
        "sam_hyeong": check_sam_hyeong(branches),
        "yuk_hae":   check_yuk_hae(branches),
        "gong_mang": check_gong_mang(day_branch, branches),
    }
