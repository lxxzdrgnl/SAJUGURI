# Saju-Calc MCP

사주팔자 **순수 계산 엔진** MCP 서버.

해석 텍스트 없이 4기둥·신살·격국·용신 등 모든 명리 계산 결과를 구조화된 JSON으로 반환합니다.

---

## 설계 원칙

- **계산만, 해석 없음**: 숫자·간지·구조만 반환. 해석 문장은 `saju-rag`가 담당
- **ephem 기반 절기**: 하드코딩 테이블 없이 실시간 천문 계산 (모든 연도 지원)
- **korean-lunar-calendar**: 300년치 테이블 없이 패키지로 음양력 변환

---

## 설치 및 실행

### uv (권장)

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync

# MCP Inspector로 개발 테스트
uv run fastmcp dev main.py

# 프로덕션 실행
uv run python main.py

# 테스트
uv run pytest tests/

# 개발 의존성 포함 설치
uv sync --group dev
```

### Docker

```bash
# 단일 서비스 실행
docker build -t saju-calc .
docker run -p 8001:8000 saju-calc

# 전체 스택 (루트 디렉토리에서)
docker compose up saju-calc

# 전체 스택 실행
docker compose up -d
```

---

## 제공 Tools (6개)

### 1. `calculate_saju`
사주팔자 전체 계산

```json
// 입력
{
  "birth_date": "1990-03-15",
  "birth_time": "14:30",
  "gender": "male",
  "calendar": "solar",
  "is_leap_month": false
}

// 출력
{
  "year_pillar":  { "stem": "경", "branch": "오", "stem_element": "금", "branch_element": "화", "yin_yang": "양" },
  "month_pillar": { "stem": "계", "branch": "묘", "stem_element": "수", "branch_element": "목", "yin_yang": "음" },
  "day_pillar":   { "stem": "경", "branch": "오", "stem_element": "금", "branch_element": "화", "yin_yang": "양" },
  "hour_pillar":  { "stem": "무", "branch": "신", "stem_element": "토", "branch_element": "금", "yin_yang": "양" },
  "wuxing_count": { "목": 1, "화": 2, "토": 1, "금": 3, "수": 1 },
  "dominant_elements": ["금"],
  "weak_elements": ["목", "수"],
  "ten_gods": ["편재", "정인", "비견", "편인"],
  "ten_gods_distribution": { "비견": 1.0, "편재": 0.7, ... },
  "sin_sals": ["yeok_ma_sal", "do_hwa_sal"],
  "branch_relations": { "sam_hap": null, "sam_hyeong": [], "yuk_hae": [] },
  "ji_jang_gan": { "year": {...}, "month": {...}, "day": {...}, "hour": {...} },
  "wol_ryeong": { "is_deuk_ryeong": false, "strength": "weak" },
  "day_master_strength": { "level": "strong", "score": 72 },
  "gyeok_guk": { "type": "bi_gyeon", "name": "비견격" },
  "yong_sin": { "primary": "화", "secondary": "목", "xi_sin": ["목"], "ji_sin": ["수"] }
}
```

---

### 2. `convert_calendar`
양력 ↔ 음력 변환

```json
// 입력
{ "date": "1990-03-15", "from_calendar": "solar", "to_calendar": "lunar", "is_leap_month": false }

// 출력
{ "original_date": "1990-03-15", "converted_date": "1990-02-19", "is_leap_month": false, "solar_term": "경칩" }
```

---

### 3. `get_dae_un`
10년 단위 대운 목록

```json
// 입력
{ "birth_date": "1990-03-15", "birth_time": "14:30", "gender": "male", "calendar": "solar", "count": 8 }

// 출력
[
  { "start_age": 3, "end_age": 12, "stem": "임", "branch": "인", "stem_element": "수", "branch_element": "목" },
  { "start_age": 13, "end_age": 22, "stem": "계", "branch": "묘", ... },
  ...
]
```

---

### 4. `get_un_flow`
세운(년) / 월운(월) / 시운(시진) / 일진(일) 간지 계산

```json
// 입력
{
  "birth_date": "1990-03-15", "birth_time": "14:30",
  "gender": "male", "calendar": "solar",
  "flow_type": "year",   // year | month | day | hour
  "target": "2025"       // year:"YYYY", month:"YYYY-MM", day:"YYYY-MM-DD", hour:"YYYY-MM-DD HH"
}

// 출력
{
  "stem": "을", "branch": "사",
  "stem_element": "목", "branch_element": "화",
  "ganji_name": "을사년",
  "interaction_with_day_master": "목생화: 일간을 설기하는 기운",
  "interaction_with_yong_sin": "화: 용신과 동일한 오행"
}
```

---

### 5. `check_compatibility`
두 사람 궁합 점수 계산

```json
// 입력
{
  "person1": { "birth_date": "1990-03-15", "birth_time": "14:30", "gender": "male", "calendar": "solar" },
  "person2": { "birth_date": "1993-07-22", "birth_time": "09:00", "gender": "female", "calendar": "solar" }
}

// 출력
{
  "total_score": 73,
  "day_pillar_score": 75,
  "element_harmony_score": 68,
  "branch_relation_score": 80,
  "ten_gods_score": 65,
  "complement_elements": ["목"],
  "conflict_branches": ["자-오"]
}
```

---

### 6. `analyze_name`
이름 오행 분석 및 용신 적합도

```json
// 입력
{ "name": "김민준", "birth_date": "1990-03-15", "birth_time": "14:30", "gender": "male", "calendar": "solar" }

// 출력
{
  "name": "김민준",
  "characters": [
    { "char": "김", "consonant": "ㄱ", "element": "목" },
    { "char": "민", "consonant": "ㅁ", "element": "토" },
    { "char": "준", "consonant": "ㅈ", "element": "금" }
  ],
  "element_distribution": { "목": 1, "토": 1, "금": 1 },
  "yong_sin_match_score": 62,
  "yong_sin": "화",
  "missing_yong_sin": true
}
```

---

## 핵심 계산 공식

### 진태양시 보정
```
실제 사주 계산 시각 = 입력 시각 - 30분
(한국 KST는 UTC+9이나 실제 천문시와 약 30분 차이)
```

### 대운 시작 나이 (만세력 공식)
```
3일 = 1년 (12개월)
1일 = 4개월
1시진(2시간) = 10일 = 40개월
→ 절기까지의 일수 × 4 = 대운 시작 개월수
```

### 월주 천간 결정 (연간→월간 규칙)
```
갑·기년 → 인월: 병간 시작
을·경년 → 인월: 무간 시작
병·신년 → 인월: 경간 시작
정·임년 → 인월: 임간 시작
무·계년 → 인월: 갑간 시작
```

---

## 프로젝트 구조

```
saju-calc/
├── main.py                  # FastMCP 서버 진입점
├── pyproject.toml           # uv 의존성 관리
├── Dockerfile
├── data/
│   ├── heavenly_stems.py    # 천간 10개
│   ├── earthly_branches.py  # 지지 12개 + 지장간 + 삼합/삼형/육해/충/합
│   └── wuxing.py            # 오행 상생/상극
├── lib/
│   ├── solar_terms.py       # ephem 24절기 계산
│   ├── calendar_converter.py
│   ├── saju.py              # 4기둥 계산
│   ├── ten_gods.py
│   ├── sin_sal.py
│   ├── day_master_strength.py
│   ├── gyeok_guk.py
│   ├── yong_sin.py
│   ├── dae_un.py
│   ├── se_un.py / wol_un.py / si_un.py
│   ├── compatibility.py
│   ├── jakmeong.py
│   └── validation.py
└── tools/                   # MCP tool 핸들러
    ├── calculate_saju.py
    ├── convert_calendar.py
    ├── get_dae_un.py
    ├── get_un_flow.py
    ├── check_compatibility.py
    └── analyze_name.py
```
