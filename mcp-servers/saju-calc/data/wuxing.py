"""
오행(五行) 정적 데이터
목·화·토·금·수 — 5개, 상생·상극 관계
"""

WUXING_DATA: dict[str, dict] = {
    "목": {
        "hanja": "木",
        "color": ["청색", "녹색"],
        "direction": "동",
        "season": "봄",
        "personality": ["인자함", "성장", "창의적", "유연함", "확장"],
    },
    "화": {
        "hanja": "火",
        "color": ["적색", "주황색", "분홍색"],
        "direction": "남",
        "season": "여름",
        "personality": ["열정적", "활동적", "밝음", "예의바름", "적극적"],
    },
    "토": {
        "hanja": "土",
        "color": ["황색", "갈색"],
        "direction": "중앙",
        "season": "환절기",
        "personality": ["신중함", "안정적", "포용력", "신뢰", "중재"],
    },
    "금": {
        "hanja": "金",
        "color": ["백색", "금색", "은색"],
        "direction": "서",
        "season": "가을",
        "personality": ["의리", "결단력", "강직함", "정의로움", "원칙적"],
    },
    "수": {
        "hanja": "水",
        "color": ["흑색", "청색", "남색"],
        "direction": "북",
        "season": "겨울",
        "personality": ["지혜로움", "깊이", "부드러움", "유연함", "침착함"],
    },
}

# 상생(相生): 목→화→토→금→수→목
WUXING_GENERATION: dict[str, str] = {
    "목": "화",
    "화": "토",
    "토": "금",
    "금": "수",
    "수": "목",
}

# 상극(相克): 목→토→수→화→금→목
WUXING_DESTRUCTION: dict[str, str] = {
    "목": "토",
    "화": "금",
    "토": "수",
    "금": "목",
    "수": "화",
}

# 역방향 — 나를 생하는 오행
_REVERSE_GENERATION: dict[str, str] = {v: k for k, v in WUXING_GENERATION.items()}
# 역방향 — 나를 극하는 오행
_REVERSE_DESTRUCTION: dict[str, str] = {v: k for k, v in WUXING_DESTRUCTION.items()}


def get_generating_element(element: str) -> str:
    """나를 생(生)하는 오행 반환"""
    return _REVERSE_GENERATION[element]


def get_generated_element(element: str) -> str:
    """내가 생(生)하는 오행 반환"""
    return WUXING_GENERATION[element]


def get_controlling_element(element: str) -> str:
    """나를 극(克)하는 오행 반환"""
    return _REVERSE_DESTRUCTION[element]


def get_controlled_element(element: str) -> str:
    """내가 극(克)하는 오행 반환"""
    return WUXING_DESTRUCTION[element]


def analyze_relation(from_element: str, to_element: str) -> str:
    """두 오행의 관계 분석"""
    if from_element == to_element:
        return "비화"  # 같은 오행
    if WUXING_GENERATION.get(from_element) == to_element:
        return "상생"  # from이 to를 생
    if WUXING_GENERATION.get(to_element) == from_element:
        return "피생"  # from이 to에게 생받음
    if WUXING_DESTRUCTION.get(from_element) == to_element:
        return "상극"  # from이 to를 극
    if WUXING_DESTRUCTION.get(to_element) == from_element:
        return "피극"  # from이 to에게 극받음
    return "중립"
