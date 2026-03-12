# Backend — FastAPI AI 파이프라인 서버

## 프로젝트 개요

기존 운세 서비스는 미리 준비된 텍스트를 조건별로 출력합니다. 사주구리는 사용자의 **사주팔자 계산 결과**와 **현재 고민**을 AI가 교차 분석해 그 사람에게만 해당하는 결론형 탭 리포트를 생성합니다.

> "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

**주요 기능**

| # | 기능 | 설명 |
|---|---|---|
| 1 | 사주 정밀 분석 | 생년월일시 + 고민 → 12단계 계산 → RAG 지식 검색 → AI 10탭 리포트 생성 |
| 2 | 궁합 | 두 사람의 사주 + Synastry 분석 → AI 궁합 리포트 |
| 3 | 오늘의 운세 | 사주 + 오늘 간지 × 일간 십성 관계 → AI 일운 리포트 |
| 4 | 한줄 상담 | 사주 + 질문 → 가중 RAG 검색 → AI 단답 상담 |
| 5 | 도시 검색 | 한국어/영문 도시 검색 → 경도·타임존·UTC 오프셋 반환 |

Engine(사주 계산)과 RAG(지식 검색)를 **Python 라이브러리로 직접 임포트** — 네트워크 오버헤드 없음.

---

## 실행

```bash
cd backend
cp .env.example .env
# .env에 GEMINI_API_KEY, DATABASE_URL 입력

# 의존성 설치
uv sync --group dev

# DB 마이그레이션 (PostgreSQL 사용 시)
uv run alembic upgrade head

# ChromaDB 초기 인덱싱 (최초 1회 또는 knowledge JSON 변경 시)
uv run python -c "from rag.ingest import ingest_all; ingest_all()"

# 서버 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 배포 주소

| 환경 | URL |
|---|---|
| 로컬 Base URL | `http://localhost:8000` |
| 로컬 Swagger UI | `http://localhost:8000/docs` |
| 로컬 Health Check | `http://localhost:8000/health` |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | FastAPI |
| Pipeline | LangChain (LCEL) |
| LLM | Gemini 2.0 Flash (기본) — Strategy Pattern |
| Output Parser | PydanticOutputParser (langchain-core) |
| Vector DB | ChromaDB (Gemini embedding-001) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| 도시 검색 | geonamescache + timezonefinder (완전 오프라인) |
| Package Manager | uv |

---

## 사용된 오픈소스 라이브러리

| 패키지 | 버전 | 라이선스 | 용도 |
|---|---|---|---|
| [FastAPI](https://github.com/tiangolo/fastapi) | ≥0.111 | MIT | REST API 프레임워크 |
| [uvicorn](https://github.com/encode/uvicorn) | ≥0.29 | BSD-3-Clause | ASGI 서버 |
| [Pydantic](https://github.com/pydantic/pydantic) | ≥2.0 | MIT | 데이터 모델·입력 검증 |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | ≥2.0 | MIT | 환경변수 설정 관리 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | ≥1.0 | BSD-3-Clause | .env 파일 로딩 |
| [LangChain](https://github.com/langchain-ai/langchain) | ≥0.2 | MIT | LLM 파이프라인 (LCEL) |
| [langchain-google-genai](https://github.com/langchain-ai/langchain-google-genai) | ≥1.0 | MIT | Gemini LLM 연동 |
| [langchain-openai](https://github.com/langchain-ai/langchain-openai) | ≥0.1 | MIT | OpenAI LLM 연동 |
| [langchain-anthropic](https://github.com/langchain-ai/langchain-anthropic) | ≥0.1 | MIT | Claude LLM 연동 |
| [google-genai](https://github.com/googleapis/python-genai) | ≥1.0 | Apache-2.0 | Gemini Embedding API |
| [ChromaDB](https://github.com/chroma-core/chroma) | ≥0.5 | Apache-2.0 | 벡터 DB (명리 지식 RAG) |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) | ≥2.0 | MIT | 비동기 ORM |
| [asyncpg](https://github.com/MagicStack/asyncpg) | ≥0.29 | Apache-2.0 | PostgreSQL 비동기 드라이버 |
| [Alembic](https://github.com/sqlalchemy/alembic) | ≥1.13 | MIT | DB 마이그레이션 |
| [ephem](https://github.com/brandon-rhodes/pyephem) | ≥4.1 | MIT | 24절기 천문 계산 (월주·대운 절기) |
| [korean-lunar-calendar](https://github.com/usingsky/korean_lunar_calendar_py) | ≥0.3.1 | MIT | 음력 ↔ 양력 변환 |
| [pytz](https://github.com/stub42/pytz) | ≥2024.1 | MIT | 표준시·시간대 처리 |
| [geonamescache](https://github.com/yaph/geonamescache) | ≥1.4 | MIT | 도시 데이터베이스 (150k+ 도시) |
| [timezonefinder](https://github.com/jannikmi/timezonefinder) | ≥6.5 | MIT | 좌표 → IANA 타임존 오프라인 변환 |
| [pytest](https://github.com/pytest-dev/pytest) | ≥8.0 | MIT | 단위 테스트 (dev) |
| [httpx](https://github.com/encode/httpx) | ≥0.27 | BSD-3-Clause | API 테스트 클라이언트 (dev) |
| [uv](https://github.com/astral-sh/uv) | — | MIT / Apache-2.0 | Python 패키지 매니저 |

---

## 환경변수

`.env.example`을 복사해 `.env`를 작성합니다.

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `LLM_PROVIDER` | — | `gemini` | LLM 선택 (`gemini` \| `openai` \| `claude`) |
| `GEMINI_API_KEY` | LLM_PROVIDER=gemini 시 필수 | — | Google AI Studio에서 발급 |
| `OPENAI_API_KEY` | LLM_PROVIDER=openai 시 필수 | — | OpenAI 플랫폼에서 발급 |
| `ANTHROPIC_API_KEY` | LLM_PROVIDER=claude 시 필수 | — | Anthropic Console에서 발급 |
| `EMBEDDING_PROVIDER` | — | `gemini` | 임베딩 모델 제공사 |
| `EMBEDDING_MODEL` | — | `gemini-embedding-001` | 임베딩 모델명 |
| `CHROMA_PATH` | — | `../mcp-servers/saju-rag/chroma_db` | ChromaDB 경로 |
| `DATABASE_URL` | PostgreSQL 사용 시 필수 | — | `postgresql+asyncpg://user:pw@host:5432/db` |
| `PORT` | — | `8000` | 서버 포트 |

---

## 엔드포인트

| 메서드 | URL | 기능 | 상태 |
|---|---|---|---|
| POST | `/api/saju/calc` | 사주팔자 12단계 계산 | ✅ 구현 완료 |
| POST | `/api/saju/report` | Engine → RAG → Writer AI 리포트 | ✅ 구현 완료 |
| GET | `/api/cities` | 도시 검색 (한국어/영문, 좌표·타임존 반환) | ✅ 구현 완료 |
| GET | `/api/saju/wol-un` | 월운 조회 | ✅ 구현 완료 |
| GET | `/api/saju/il-jin` | 일진 달력 조회 | ✅ 구현 완료 |
| GET | `/api/saju/yeon-un` | 연운 조회 | ✅ 구현 완료 |
| POST | `/api/compatibility` | 궁합 분석 | 구현 예정 |
| POST | `/api/daily` | 오늘의 운세 | 구현 예정 |
| POST | `/api/question` | 한줄 상담 | 구현 예정 |
| GET | `/health` | 서버 상태 확인 | ✅ 구현 완료 |
| GET | `/docs` | Swagger UI | ✅ |

---

## 모듈 구조

```
backend/
├── main.py                         # FastAPI 앱 진입점
├── pyproject.toml
├── .env.example
│
├── engine/                         # 만세력 계산 엔진
│   ├── calc/                       # 순수 계산 모듈 (15개)
│   │   ├── saju.py                 # 4기둥 계산 (연·월·일·시주)
│   │   ├── ten_gods.py             # 십성·12운성 계산
│   │   ├── sin_sal.py              # 신살 판단 (10종)
│   │   ├── day_master_strength.py  # 일간 강약 점수화
│   │   ├── gyeok_guk.py            # 격국 판단 (13종)
│   │   ├── yong_sin.py             # 용신 선정 (억부/조후/통관)
│   │   ├── dae_un.py               # 대운 계산 (3일=1년 공식)
│   │   ├── solar_terms.py          # ephem 24절기 실시간 계산
│   │   ├── calendar_converter.py   # 음양력 변환 (korean-lunar-calendar)
│   │   └── validation.py           # 입력 검증
│   │
│   ├── analysis/                   # 후처리 분석 파이프라인 (6개)
│   │   ├── structure_patterns.py   # 구조 패턴 감지 (15종)
│   │   ├── dynamics.py             # 기둥 간 동역학 (천간합·통근·오행흐름)
│   │   ├── synergy.py              # 구조패턴 × 동역학 교차 시너지 (30규칙)
│   │   ├── behavior_synthesizer.py # 십성 분포 → 행동 벡터 합성
│   │   ├── context_ranker.py       # RAG 우선순위화 (primary 3 + secondary 2)
│   │   └── life_domain_mapper.py   # career·relationship·wealth·personality 분류
│   │
│   ├── handlers/                   # 기능별 계산 핸들러
│   │   ├── calculate_saju.py       # 12단계 파이프라인 전체 실행
│   │   ├── get_wol_un.py           # 월운 핸들러
│   │   ├── get_il_jin.py           # 일진 핸들러
│   │   └── get_yeon_un.py          # 연운 핸들러
│   │
│   └── data/                       # 정적 명리학 데이터
│       ├── heavenly_stems.py       # 천간 10개
│       ├── earthly_branches.py     # 지지 12개 (지장간·충합형해)
│       ├── wuxing.py               # 오행 상생·상극 관계
│       └── timezone_history.py     # 역사적 한국 표준시 + 진태양시 보정
│
├── rag/                            # ChromaDB 기반 명리학 지식 검색
│   ├── db.py                       # ChromaDB 연결·검색
│   ├── ingest.py                   # 지식 JSON → ChromaDB 인덱싱
│   ├── search.py                   # 컨텍스트 기반 검색 핸들러
│   ├── providers.py                # Embedding Strategy Pattern
│   └── knowledge/                  # 명리학 지식 JSON (105개 문서)
│
├── llm/                            # Writer LLM + 파이프라인
│   ├── providers.py                # LLM Strategy Pattern (Gemini/OpenAI/Claude)
│   ├── rag_builder.py              # 사주 결과 → RAG 컨텍스트 조립
│   ├── prompts.py                  # 시스템 프롬프트 + 사용자 메시지 포맷터
│   ├── writer.py                   # PydanticOutputParser 기반 리포트 생성
│   └── pipelines/
│       └── saju_report.py          # Engine → RAG → Writer 파이프라인
│
├── routers/                        # FastAPI 라우터
│   ├── saju.py                     # /api/saju/*
│   └── cities.py                   # GET /api/cities (도시 검색)
│
├── schemas/                        # Pydantic 요청/응답 스키마
│   ├── saju.py                     # SajuCalcRequest / SajuCalcResponse
│   └── report.py                   # SajuReportRequest / WriterOutput
│
├── db/                             # 데이터베이스
│   ├── models.py                   # SQLAlchemy 모델 (Report·User)
│   └── session.py                  # async 세션 팩토리
│
├── core/                           # 설정·에러코드·커스텀 예외
├── middleware/                     # 요청/응답 로깅 미들웨어
└── dependencies/                   # FastAPI 의존성
```

---

## Engine — 사주팔자 12단계 파이프라인

`POST /api/saju/calc` 한 번 호출로 순차 실행됩니다.

```
① 4기둥          연·월·일·시주 (진태양시 보정 포함)
② 십성·12운성    기둥별 태그
③ 신살           역마·도화·화개·귀문관살 등 10종
④ 일간 강약      점수화 (very_strong/strong/medium/weak/very_weak)
⑤ 격국           13종
⑥ 용신           억부/조후/통관
⑦ 대운           3일=1년 공식 (10구간)
⑧ 음양 비율      8글자 기준
⑨ 구조패턴       15종 + 동역학(천간합·통근·오행흐름) + 시너지(30규칙)
⑩ 행동프로파일   십성분포 → behavior_vector
⑪ 컨텍스트랭킹   primary 3 + secondary 2
⑫ 생활도메인     career·relationship·wealth·personality
```

### 핵심 계산 공식

| 항목 | 공식 |
|---|---|
| 진태양시 보정 | 동경 127° 기준, 역사적 표준시 자동 적용 (통상 -30~-32분) |
| 연주 기준 | 1984년 = 甲子년, `(year-4)%10` = 천간, `(year-4)%12` = 지지 |
| 일주 기준일 | 1900-01-01 = 甲戌일 (stemIdx=0, branchIdx=10) |
| 월주 천간 | 갑·기년→丙寅, 을·경년→戊寅, 병·신년→庚寅, 정·임년→壬寅, 무·계년→甲寅 |
| 시주 천간 | `(일간index × 2 + 시지index) % 10` |
| 대운 공식 | 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세 |
| 24절기 | ephem 라이브러리 실시간 천문 계산 |
| 음력 변환 | korean-lunar-calendar 패키지 |

---

## 도시 검색 API

### `GET /api/cities?q=검색어`

geonamescache(150k+ 도시) + timezonefinder를 이용한 완전 오프라인 도시 검색.

- **한글 입력** → GeoNames alternateNames에서 한국어 매칭
- **영문 입력** → GeoNames name/asciiname prefix 매칭
- 반환: 경도, IANA 타임존, UTC 오프셋(분), 국가명

```bash
# 한국어 검색
curl "http://localhost:8000/api/cities?q=서울"

# 영문 검색
curl "http://localhost:8000/api/cities?q=London"
```

```json
[
  {
    "label": "서울",
    "sublabel": "Seoul, South Korea",
    "longitude": 126.9784,
    "utc_offset": 540,
    "timezone": "Asia/Seoul",
    "is_korea": true
  }
]
```

---

## Writer LLM Strategy Pattern

```
.env: LLM_PROVIDER=gemini (기본) | openai | claude

지원 모델
  gemini → gemini-2.0-flash
  openai → gpt-4o
  claude → claude-sonnet-4-6
```

파싱 실패 시 JSON 수정 프롬프트로 자동 재시도합니다.

---

## RAG 지식 베이스 (ChromaDB)

| 컬렉션 | 문서 수 | 내용 |
|---|---|---|
| `ilju` | 60 | 60갑자 일주론 — 아키타입·직업·연애·취약점 |
| `ten_gods` | 10 | 십성(十星) — 비견~정인 특성 |
| `sin_sal` | 가변 | 신살 — 역마·도화·귀문관살 등 |
| `structure_patterns` | 가변 | 구조 패턴 15종 해석 |
| `dynamics` | 가변 | 동역학 — 천간합·충·삼합 해석 |
| `wuxing` | 가변 | 오행 상생·상극 해석 |

Embedding: Gemini embedding-001

```bash
# 최초 실행 또는 knowledge JSON 변경 시
uv run python -c "from rag.ingest import ingest_all; ingest_all()"
```
