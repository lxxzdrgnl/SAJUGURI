# 사주구리 - AI 사주 상담 서비스

## 1. 프로젝트 핵심 컨셉: "Headline-Driven Insights"

AI가 사용자의 사주와 현재 고민을 분석하여 **오직 그 사람만을 위한 결론형 탭 리포트**를 생성합니다.

> "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 2. 전체 시스템 아키텍처

Engine(계산)과 RAG(지식)를 **Python 라이브러리로 직접 임포트**하는 2-Tier 구조입니다.
MCP 프로토콜은 사용하지 않습니다.

```
Frontend (Vue.js 3 / Nuxt.js)
    │  생년월일시 + 성별 + 고민
    ▼
Backend (FastAPI)
    ├─→ engine/        만세력 계산 (4기둥·십성·격국·용신·대운·분석)
    ├─→ rag/           ChromaDB 명리 지식 검색
    ├─→ pipelines/     기능별 파이프라인 조합
    └─→ llm/           Writer Agent (LangChain + PydanticOutputParser)
    ▼
Frontend
    완성된 JSON 1회 반환 → 탭 클릭 = 단순 뷰 전환
```

---

## 3. 4가지 기능 및 파이프라인

### 사주 정밀 분석 `POST /api/saju/calc`
```
Engine.calculate_saju()
  → context_ranking + life_domains
  → RAG 검색 (도메인별 청크)
  → Context Filter (primary 우선 + concern 시맨틱 merge)
  → Writer → 10개 결론형 탭
```

### 궁합 `POST /api/compatibility`
```
Engine.calculate_saju(person1) + Engine.calculate_saju(person2)
  → Synastry Engine (천간합·월지삼합충·용신보완·십성패턴)
  → RAG 검색 (interaction_tags)
  → Writer → 궁합 리포트 (총점 + 항목별 분석)
```

### 오늘의 운세 `POST /api/daily`
```
Engine.calculate_saju() + Engine.get_un_flow(today)
  → Daily Flow (오늘 천간 × 일간 십성, 오늘 지지 × 월지 충합)
  → RAG 검색 (daily_tags)
  → Writer → 오늘 운세 (1탭, 간결)
```

### 한줄 상담 `POST /api/question`
```
Engine.calculate_saju() → behavior_profile + core_keywords
  → 가중 RAG 검색 (question 시맨틱 + saju keywords boost)
  → Writer → 단답형 상담 (1탭, 500자)
```

---

## 4. Engine 12단계 파이프라인

`calculate_saju()` 한 번 호출로 순차 실행:

```
① 4기둥          연·월·일·시주 (진태양시 -30분 보정)
② 십성·12운성    기둥별 태그
③ 신살           역마·도화·화개·귀문관살 등 10종
④ 일간 강약      점수화 (strong/medium/weak)
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

## 5. RAG 지식 베이스 (ChromaDB)

| 컬렉션 | 문서 수 | 내용 |
|---|---|---|
| ilju | 60 | 60갑자 일주론 (성격·직업·연애) |
| ten_gods | 10 | 십성 해석 (비견~정인) |
| sin_sal | 가변 | 신살 의미 (역마·도화·귀문관살 등) |
| structure_patterns | 가변 | 구조 패턴 해석 |
| dynamics | 가변 | 동역학 해석 |
| wuxing | 가변 | 오행 상생·상극 해석 |

Embedding: Gemini embedding-001

---

## 6. 프로젝트 구조

```
SajuNara/
├── CLAUDE.md
├── README.md
├── frontend/           # Vue.js 3 + Nuxt.js (구현 예정)
└── backend/
    ├── engine/
    │   ├── calc/       # 순수 계산 (15개 모듈)
    │   ├── analysis/   # 후처리 분석 (6개 모듈)
    │   ├── handlers/   # 기능별 핸들러
    │   └── data/       # 정적 명리학 데이터
    ├── rag/            # ChromaDB 검색 + knowledge JSON
    ├── llm/            # Writer LLM (구현 예정)
    ├── pipelines/      # 기능별 파이프라인 (구현 예정)
    ├── routers/        # FastAPI 라우터
    ├── schemas/        # Pydantic 스키마
    ├── db/             # SQLAlchemy 모델·세션
    ├── core/           # pydantic-settings 설정
    └── dependencies/   # FastAPI 의존성
```

---

## 7. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+ (Main), TypeScript (Frontend) |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | Gemini 2.0 Flash (기본) — Strategy Pattern (OpenAI·Claude 교체 가능) |
| Output Parser | PydanticOutputParser + OutputFixingParser |
| Vector DB | ChromaDB (Gemini embedding-001) |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Package Manager | uv (Python), pnpm (Node.js) |
| DevOps | Docker, Docker Compose |

---

## 8. 개발 원칙

- Engine과 RAG는 Python 라이브러리로 직접 임포트한다 (MCP 없음).
- 모든 탭 내용은 **한 번에 생성**하여 완성된 JSON을 반환한다 (탭 클릭 = 뷰 전환만).
- 헤드라인은 반드시 **결론형 문장**으로 생성한다 (단순 카테고리명 금지).
- 모든 명리 해석은 RAG 지식 베이스에 근거하여 생성한다.
- LLM은 Strategy Pattern으로 교체 가능하게 설계한다.

---

## 9. 구현 TODO (포스텔러 수준 만세력 리포트)

목표: 포스텔러 만세력 2.2와 동등한 사주 리포트 + AI 탭 리포트

### Phase 1 — 백엔드 엔진 보완

- [x] **12신살 (기둥별)** — 지살·겁살·망신살·육해살·재살·천살·년살·월살·일살·시살 per-pillar 추가
- [x] **신살 종류 확장** — 현침살·태극귀인·문곡귀인·관귀학관·홍염살·고신살·월덕귀인·황은대사 (+8종)
  > **주의**: 신살 확장은 프론트 표시용. RAG 검색·Writer 입력은 기존 context_ranking(priority high/medium 기준) 그대로 유지.
- [x] **공망(空亡) 계산** — 일주 기준 공망 지지 2개 + 해당 기둥 반환 (`gong_mang` 최상위 필드)
- [x] **득령/득지/득시/득세 boolean 4개** — day_master_strength 출력에 추가
- [x] **신강/신약 8단계** — 극약·태약·신약·중화신약·중화신강·신강·태강·극왕 + 백분율
- [x] **합충 위치 정보** — dynamics.active_relations에 기둥 위치 태그 이미 포함
- [x] **월운 API** — `GET /api/saju/wol-un?year=&day_stem=`
- [x] **일진 달력 API** — `GET /api/saju/il-jin?year=&month=`
- [x] **용신 표기** — `yong_sin_label` 필드 추가 (억부용신/통관용신)

### Phase 2 — 프론트엔드 세팅

- [x] **Nuxt.js 3 프로젝트 초기화** — frontend/ 디렉토리, Tailwind CSS, Pinia
- [x] **입력 폼** — 생년월일시·음양력·윤달·성별 선택 (components/saju/InputForm.vue)
- [x] **Pinia store** — saju 계산 결과 상태 관리 (stores/saju.ts)
- [x] **API 클라이언트** — backend `/api/saju/calc` 호출 래퍼 (composables/useSajuApi.ts)

### Phase 3 — 만세력 리포트 컴포넌트

- [ ] **SajuTable** — 4기둥 그리드 (천간·십성·지지·십성·지장간·12운성·12신살, 음양 색상)
- [ ] **HapChungPanel** — 합충 탭 버튼 (천간합·지지육합·삼합·방합·충·공망·형·파·해·원진) + 해당 기둥 하이라이트
- [ ] **WuxingPentagram** — 오행 오각형 SVG (상생 파란 화살표·상극 빨간 별, 원 비율 채우기)
- [ ] **WuxingDonutChart** — 오행 도넛 차트 (Chart.js)
- [ ] **SipseongDonutChart** — 십성 도넛 차트
- [ ] **StrengthChart** — 신강/신약 8단계 분포 라인 차트 + 득령/득지/득시/득세 뱃지
- [ ] **YongSinBadge** — 용신·희신·기신 표시
- [ ] **DaeUnSlider** — 대운 수평 스크롤 (천간/지지 칩, 십성·12운성 레이블)
- [ ] **YeonUnSlider** — 연운 수평 스크롤
- [ ] **WolUnSlider** — 월운 수평 스크롤
- [ ] **IlJinCalendar** — 일진 달력 (월 네비게이션, 일별 간지·음력 날짜)

### Phase 4 — AI 탭 리포트 (Headline-Driven Insights)

- [ ] **Writer LLM 세팅** — llm/providers.py Gemini 연결
- [ ] **프롬프트 작성** — 사주 calc 결과 + 고민 → 10개 결론형 헤드라인
- [ ] **PydanticOutputParser** — ReportOutput(tabs: list[TabContent]) 스키마
- [ ] **사주 분석 파이프라인** — Engine → RAG → Context Filter → Writer
- [ ] **AI 리포트 탭 UI** — 헤드라인 탭 클릭 → 상세 내용 즉시 전환
- [ ] **궁합 파이프라인** (Phase 4 후반)
- [ ] **오늘의 운세 파이프라인** (Phase 4 후반)
- [ ] **한줄 상담 파이프라인** (Phase 4 후반)

### Phase 5 — DB·공유·인증

- [ ] **PostgreSQL 연결** — SQLAlchemy async 세션
- [ ] **Report 저장** — 계산 결과 + AI 출력 저장
- [ ] **공유 링크** — `GET /r/{share_token}`
- [ ] **JWT 인증** (선택)

---

## 10. 핵심 계산 공식

- **진태양시 보정**: -30분 (동경 127° 보정, 역사적 표준시 자동 적용)
- **연주 기준**: 1984년 = 갑자년, `(year-4)%10` = 천간, `(year-4)%12` = 지지
- **일주 기준일**: 1900-01-01 = 갑술일 (stemIdx=0, branchIdx=10)
- **월주 천간**: 갑·기년→병인월, 을·경년→무인월, 병·신년→경인월, 정·임년→임인월, 무·계년→갑인월
- **시주 천간**: `(일간index*2 + 시지index) % 10`
- **대운 공식**: 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세
- **24절기**: ephem 라이브러리 실시간 천문 계산
- **음력 변환**: korean-lunar-calendar 패키지
