# 사주구리

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.x-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-Writer_LLM-4285F4?style=flat-square&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?style=flat-square)


**AI가 당신의 사주(四柱)와 오늘의 고민을 함께 읽어드립니다.**

> "재물운" (X)
> "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## Production

- Frontend: https://sajuguri.rheon.kr
- Backend API: https://api-sajuguri.rheon.kr
- Swagger UI: https://api-sajuguri.rheon.kr/docs
- Health Check: https://api-sajuguri.rheon.kr/health

---

## 사주팔자(四柱八字)란?

태어난 **연·월·일·시** 네 기둥(四柱), 여덟 글자(八字)로 이루어진 동양 명리학의 핵심입니다.

| 기둥 | 의미 |
|---|---|
| 연주(年柱) | 조상·초년운 |
| 월주(月柱) | 부모·청장년운 |
| 일주(日柱) | 본인·배우자·중년운 |
| 시주(時柱) | 자녀·노년운 |

---

## 프로젝트 개요

기존 운세 서비스는 미리 준비된 텍스트를 조건별로 출력합니다. 사주구리는 사용자의 **사주팔자 계산 결과**와 **현재 고민**을 AI가 교차 분석해 그 사람에게만 해당하는 결론형 탭 리포트를 생성합니다.

**주요 기능**

| # | 기능 | 엔드포인트 | 파이프라인 |
|---|---|---|---|
| 1 | 사주 정밀 분석 | `POST /api/saju/calc` | Engine → RAG → Context Filter → Writer (10탭) |
| 2 | 궁합 | `POST /api/compatibility` | Engine×2 → Synastry → RAG → Writer |
| 3 | 오늘의 운세 | `POST /api/daily` | Engine + 오늘간지 → Daily Tags → RAG → Writer |
| 4 | 한줄 상담 | `POST /api/question` | Engine → 가중 RAG 검색 → Writer |

---

## 핵심 컨셉: Headline-Driven Insights

사주 계산 결과와 사용자의 실제 고민을 AI가 교차 분석해 **오직 당신만을 위한 결론형 탭 리포트**를 생성합니다.

```
입력: "2001-08-17 11:00 남성 + 회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 임자일주, 가장 차가운 물이 가장 깊은 곳에 있습니다 — 그 고집이 상사와 정면충돌
  탭 2. 식상생재격 + 현 대운 계사(癸巳) — 창의적 실행이 곧 수입이 되는 시기
  탭 3. 용신 목(木)·화(火)가 강한 콘텐츠·IT 계열에서 귀문관살의 직관이 빛을 발함
  탭 4. 귀문관살 + 상관패인 — 날카로운 비판 지성이 무기이자 조직 내 갈등의 씨앗
  ...
```

---

## 레이어별 상세 문서

| 레이어 | 경로 | 문서 |
|---|---|---|
| Frontend | [frontend/](./frontend) | [frontend/README.md](./frontend/README.md) |
| Backend | [backend/](./backend) | [backend/README.md](./backend/README.md) |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | Gemini 2.0 Flash (기본) — Strategy Pattern (OpenAI·Claude 교체 가능) |
| Output Parser | PydanticOutputParser (langchain-core) |
| Vector DB | ChromaDB (Gemini embedding-001, 105개 문서) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| 도시 검색 | geonamescache + timezonefinder (오프라인, 150k+ 도시) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose |

---

## 사용된 오픈소스 라이브러리

### Backend (Python)

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
| [ephem](https://github.com/brandon-rhodes/pyephem) | ≥4.1 | MIT | 24절기 천문 계산 |
| [korean-lunar-calendar](https://github.com/usingsky/korean_lunar_calendar_py) | ≥0.3.1 | MIT | 음력 ↔ 양력 변환 |
| [pytz](https://github.com/stub42/pytz) | ≥2024.1 | MIT | 표준시·시간대 처리 |
| [geonamescache](https://github.com/yaph/geonamescache) | ≥1.4 | MIT | 도시 데이터베이스 (150k+ 도시) |
| [timezonefinder](https://github.com/jannikmi/timezonefinder) | ≥6.5 | MIT | 좌표 → IANA 타임존 오프라인 변환 |
| [pytest](https://github.com/pytest-dev/pytest) | ≥8.0 | MIT | 단위 테스트 |
| [httpx](https://github.com/encode/httpx) | ≥0.27 | BSD-3-Clause | API 테스트 클라이언트 |
| [uv](https://github.com/astral-sh/uv) | — | MIT / Apache-2.0 | Python 패키지 매니저 |

### Frontend (TypeScript)

| 패키지 | 라이선스 | 용도 |
|---|---|---|
| [Vue.js 3](https://github.com/vuejs/core) | MIT | UI 프레임워크 |
| [Nuxt.js 3](https://github.com/nuxt/nuxt) | MIT | SSR/SSG 프레임워크 |
| [Pinia](https://github.com/vuejs/pinia) | MIT | 상태 관리 |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) | MIT | CSS 유틸리티 프레임워크 |
| [Chart.js](https://github.com/chartjs/Chart.js) | MIT | 오행·십성 도넛 차트 |
| [pnpm](https://github.com/pnpm/pnpm) | MIT | Node.js 패키지 매니저 |

---

## 빠른 시작

### Docker로 한번에 실행 (권장)

```bash
# 저장소 클론
git clone <repo>
cd SajuNara

# 환경변수 설정
cp backend/.env.example backend/.env   # GEMINI_API_KEY 입력
cp frontend/.env.example frontend/.env # 기본값 사용 가능

# 전체 스택 실행 (postgres + backend + frontend)
docker compose up --build

# 백그라운드 실행
docker compose up --build -d

# 종료
docker compose down
```

서비스가 모두 올라오면:
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000

### 로컬 개발 환경

```bash
# 저장소 클론
git clone <repo>
cd SajuNara

# 백엔드
cd backend
cp .env.example .env        # GEMINI_API_KEY, DATABASE_URL 입력
uv sync --group dev
uv run alembic upgrade head
uv run python -c "from rag.ingest import ingest_all; ingest_all()"
uv run uvicorn main:app --reload --port 8000

# 프론트엔드 (별도 터미널)
cd frontend
cp .env.example .env        # NUXT_PUBLIC_API_BASE=http://localhost:8000
pnpm install
pnpm dev
```

---

## 아키텍처

```
Frontend (Vue.js 3 + Nuxt.js)  :3000
    │  생년월일시 + 성별 + 고민
    ▼
Backend (FastAPI)  :8000
    │
    ├─→ [1] Engine (engine/)
    │         4기둥 · 오행 · 십성 · 신살 · 격국 · 용신 · 대운
    │         behavior_profile · context_ranking · life_domains
    │         ↓
    ├─→ [2] RAG (rag/)
    │         context_ranking + life_domains → ChromaDB 검색
    │         → 명리 해석 텍스트 청크 반환
    │         ↓
    └─→ [3] Writer (llm/)
              calc 데이터 + rag 지식 + 고민
              → 결론형 헤드라인 + 탭 본문 일괄 생성
    ▼
Frontend
    완성된 리포트 전체 수신 → 탭 클릭 시 즉시 전환
```

---

## 코드 구조

```
SajuNara/
├── frontend/               # Vue.js 3 + Nuxt.js → frontend/README.md
└── backend/                # FastAPI + AI 파이프라인 → backend/README.md
    ├── engine/             # 만세력 계산 엔진 (12단계 파이프라인)
    ├── rag/                # ChromaDB 명리학 지식 검색
    ├── llm/                # Writer LLM + 파이프라인
    ├── routers/            # FastAPI 라우터 (saju, cities)
    ├── schemas/            # Pydantic 요청/응답 스키마
    ├── core/               # 설정·에러코드·커스텀 예외
    ├── middleware/         # 요청/응답 로깅
    ├── db/                 # SQLAlchemy 모델·세션
    └── dependencies/       # FastAPI 의존성
```

---

## 환경변수

### Backend (`backend/.env`)

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `LLM_PROVIDER` | — | `gemini` | LLM 선택 (`gemini` \| `openai` \| `claude`) |
| `GEMINI_API_KEY` | gemini 시 필수 | — | Google AI Studio 발급 |
| `OPENAI_API_KEY` | openai 시 필수 | — | OpenAI 플랫폼 발급 |
| `ANTHROPIC_API_KEY` | claude 시 필수 | — | Anthropic Console 발급 |
| `CHROMA_PATH` | — | `../mcp-servers/saju-rag/chroma_db` | ChromaDB 경로 |
| `DATABASE_URL` | PostgreSQL 사용 시 필수 | — | `postgresql+asyncpg://user:pw@host:5432/db` |

### Frontend (`frontend/.env`)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | 백엔드 API 주소 |

---

## Calc Engine 12단계 파이프라인

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

---

## 스크린샷

![스크린샷](./screenshot/screenshot_260311.png)
