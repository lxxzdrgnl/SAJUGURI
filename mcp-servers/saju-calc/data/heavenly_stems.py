"""
천간(天干) 정적 데이터
갑·을·병·정·무·기·경·신·임·계 — 10개
"""

HEAVENLY_STEMS: list[dict] = [
    {"korean": "갑", "hanja": "甲", "element": "목", "yin_yang": "양", "index": 0},
    {"korean": "을", "hanja": "乙", "element": "목", "yin_yang": "음", "index": 1},
    {"korean": "병", "hanja": "丙", "element": "화", "yin_yang": "양", "index": 2},
    {"korean": "정", "hanja": "丁", "element": "화", "yin_yang": "음", "index": 3},
    {"korean": "무", "hanja": "戊", "element": "토", "yin_yang": "양", "index": 4},
    {"korean": "기", "hanja": "己", "element": "토", "yin_yang": "음", "index": 5},
    {"korean": "경", "hanja": "庚", "element": "금", "yin_yang": "양", "index": 6},
    {"korean": "신", "hanja": "辛", "element": "금", "yin_yang": "음", "index": 7},
    {"korean": "임", "hanja": "壬", "element": "수", "yin_yang": "양", "index": 8},
    {"korean": "계", "hanja": "癸", "element": "수", "yin_yang": "음", "index": 9},
]

# O(1) 조회용 dict
STEMS_BY_INDEX: dict[int, dict] = {s["index"]: s for s in HEAVENLY_STEMS}
STEMS_BY_KOREAN: dict[str, dict] = {s["korean"]: s for s in HEAVENLY_STEMS}
STEMS_BY_HANJA: dict[str, dict] = {s["hanja"]: s for s in HEAVENLY_STEMS}

# 순서 리스트 (인덱스 계산용)
STEMS_ORDER: list[str] = [s["korean"] for s in HEAVENLY_STEMS]


def get_stem_by_index(index: int) -> dict:
    """인덱스로 천간 조회 (음수·범위 초과 자동 보정)"""
    return STEMS_BY_INDEX[index % 10]


def get_stem_by_korean(korean: str) -> dict:
    return STEMS_BY_KOREAN[korean]
