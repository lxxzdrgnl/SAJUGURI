# 사주구리

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white)
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

## 주요 기능

| 기능 | 엔드포인트 | 상태 |
|---|---|---|
| 만세력 정밀 분석 | `POST /api/saju/calc` | 구현 (AI 탭 리포트 개발 중) |
| 오늘의 운세 | `POST /api/saju/daily` | 구현 |
| 한줄 상담 | `POST /api/question` | 구현 |
| 궁합 | `POST /api/compatibility` | 개발 예정 |

---

## 핵심 컨셉: Headline-Driven Insights

사주 계산 결과와 사용자의 실제 고민을 AI가 교차 분석해 **오직 당신만을 위한 결론형 탭 리포트**를 생성합니다.

```
입력: "2001-08-17 11:00 남성 + 회사 상사와 갈등이 심해 이직을 고민 중입니다"

출력:
  탭 1. 임자일주, 가장 차가운 물이 가장 깊은 곳에 있습니다 — 그 고집이 상사와 정면충돌
  탭 2. 식상생재격 + 현 대운 계사(癸巳) — 창의적 실행이 곧 수입이 되는 시기
  탭 3. 용신 목(木)·화(火)가 강한 콘텐츠·IT 계열에서 귀문관살의 직관이 빛을 발함
  ...
```

기존 사주 앱은 "재물운: 보통", "건강운: 좋음" 식의 카테고리 레이블을 탭 제목으로 쓴다. 누구에게나 동일한 카테고리 구조를 강요하므로 이 사람만의 구조적 특성을 전달하지 못한다. 헤드라인을 결론형 문장으로 만들면 탭 목록 자체가 이미 리포트가 된다 — 클릭하기 전에도 "내 얘기"임을 인식할 수 있어야 한다.

GPT-4o에게 사주만 던지면 그럴듯한 문장이 나오지만 명리학적 근거가 없다. 용신 오행에 맞는 직업군, 일주별 연애 패턴, 신살의 구체적 발현 방식은 수백 년간 정리된 명리학 지식이고 LLM 사전학습 데이터에는 충분히 들어있지 않다. RAG로 검증된 지식을 컨텍스트로 주입한 뒤 LLM이 그 근거 위에서 문장을 생성하게 한다 — 해석의 정확도는 RAG가, 표현의 질은 LLM이 담당한다.

탭을 스트리밍으로 하나씩 생성하면 탭 간 맥락 일관성이 깨진다. 탭 1에서 "이직을 권한다"고 했다가 탭 3에서 "현 직장을 유지하라"는 결론이 나올 수 있다. 한 번의 LLM 호출로 모든 탭을 `PydanticOutputParser`로 구조화해 반환하면 탭 간 논리 일관성이 보장되고, 프론트엔드는 탭 클릭 시 추가 API 호출 없이 즉시 전환만 한다.

---

## 레이어별 상세 문서

| 레이어 | 문서 |
|---|---|
| Frontend | [frontend/README.md](./frontend/README.md) |
| Backend | [backend/README.md](./backend/README.md) |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+, TypeScript |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | OpenAI GPT-4o (Writer) — Strategy Pattern (Gemini·Claude 교체 가능) |
| Embedding | Gemini embedding-001 (ChromaDB) |
| Vector DB | ChromaDB |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose |

---

## 빠른 시작

### Docker (권장)

```bash
git clone <repo> && cd SajuNara

cp backend/.env.example backend/.env   # OPENAI_API_KEY, GEMINI_API_KEY 입력
cp frontend/.env.example frontend/.env

docker compose up --build
```

- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000

### 로컬 개발

```bash
# 백엔드
cd backend
cp .env.example .env
uv sync --group dev
uv run alembic upgrade head
uv run python -c "from rag.ingest import ingest_all; ingest_all()"   # 최초 1회: ChromaDB 인덱싱
uv run uvicorn main:app --reload --port 8000

# 프론트엔드 (별도 터미널)
cd frontend
cp .env.example .env
pnpm install && pnpm dev
```

---

## 사용된 오픈소스 라이브러리

### Backend (Python)

| 패키지 | 라이선스 | 용도 |
|---|---|---|
| [FastAPI](https://github.com/tiangolo/fastapi) | MIT | REST API 프레임워크 |
| [LangChain](https://github.com/langchain-ai/langchain) | MIT | LLM 파이프라인 (LCEL) |
| [ChromaDB](https://github.com/chroma-core/chroma) | Apache-2.0 | 벡터 DB |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) | MIT | 비동기 ORM |
| [Alembic](https://github.com/sqlalchemy/alembic) | MIT | DB 마이그레이션 |
| [ephem](https://github.com/brandon-rhodes/pyephem) | MIT | 24절기 천문 계산 |
| [korean-lunar-calendar](https://github.com/usingsky/korean_lunar_calendar_py) | MIT | 음력 ↔ 양력 변환 |
| [geonamescache](https://github.com/yaph/geonamescache) | MIT | 도시 데이터베이스 |
| [timezonefinder](https://github.com/jannikmi/timezonefinder) | MIT | 좌표 → 타임존 변환 |

### Frontend (TypeScript)

| 패키지 | 라이선스 | 용도 |
|---|---|---|
| [Vue.js 3](https://github.com/vuejs/core) | MIT | UI 프레임워크 |
| [Nuxt.js 3](https://github.com/nuxt/nuxt) | MIT | SSR 프레임워크 |
| [Pinia](https://github.com/vuejs/pinia) | MIT | 상태 관리 |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) | MIT | CSS 유틸리티 |
| [Chart.js](https://github.com/chartjs/Chart.js) | MIT | 도넛 차트 |

---

## 스크린샷

![스크린샷](./screenshot/screenshot_260311.png)
