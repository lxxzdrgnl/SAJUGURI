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

| 기능 | 엔드포인트 | 상태 |
|---|---|---|
| 만세력 정밀 분석 | `POST /api/saju/calc` | ✅ 엔진 완료, AI 탭 미구현 |
| 오늘의 운세 | `POST /api/saju/daily` | ✅ 완료 (AI 없는 명리 기반) |
| 한줄 상담 | `POST /api/question` | ✅ 완료 (OpenAI GPT-4o) |
| 궁합 | `POST /api/compatibility` | ❌ 미구현 |

---

## 4. Engine 12단계 파이프라인 (`engine/calc/`)

`calculate_saju()` 한 번 호출로 순차 실행:

```
① 4기둥          연·월·일·시주 (진태양시 -30분 보정)
② 십성·12운성    기둥별 태그
③ 신살           역마·도화·화개·귀문관살 등 18종
④ 일간 강약      점수화 + 8단계 + 득령/득지/득시/득세
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
| sin_sal | 가변 | 신살 의미 |
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
├── frontend/               # Vue.js 3 + Nuxt.js ✅
└── backend/
    ├── engine/
    │   ├── calc/           # 순수 계산 (15개 모듈) ✅
    │   ├── analysis/       # 후처리 분석 ✅
    │   └── data/           # 정적 명리학 데이터 ✅
    ├── rag/                # ChromaDB 검색 + knowledge JSON ✅
    ├── llm/                # Writer LLM (미구현)
    ├── pipelines/          # 기능별 파이프라인 (미구현)
    ├── routers/            # FastAPI 라우터 ✅
    ├── schemas/            # Pydantic 스키마 ✅
    ├── db/                 # SQLAlchemy 모델·세션 ✅
    ├── core/               # pydantic-settings 설정 ✅
    └── dependencies/       # FastAPI 의존성 ✅
```

---

## 7. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.10+ (Main), TypeScript (Frontend) |
| Frontend | Vue.js 3, Pinia, Nuxt.js, Tailwind CSS |
| Backend | FastAPI, LangChain (LCEL) |
| AI / LLM | OpenAI GPT-4o (Writer) — Strategy Pattern (Gemini·Claude 교체 가능) |
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

## 8-1. 백엔드 아키텍처 패턴 (필수 준수)

### 3-레이어 구조

```
Router  →  Service  →  CRUD  →  DB
```

| 레이어 | 책임 | 금지 |
|---|---|---|
| **Router** | HTTP 입출력, 의존성 주입만 | try/except, DB 직접 접근, 비즈니스 로직 |
| **Service** | 비즈니스 흐름 제어, 예외 변환, 단일 commit | 여러 번 commit |
| **CRUD** | DB 접근만 (select/add/flush) | 비즈니스 규칙, commit (단발 연산 제외) |

### CRUD 작성 규칙

- **읽기 전용 함수**: 그냥 `return`. commit/flush 없음.
- **멀티스텝 연산의 쓰기 함수**: `db.add()` + `db.flush()` + `db.refresh()` 까지만. **commit은 Service가 마지막에 한 번만.**
- **단발 단순 쓰기** (logout, share 생성 등): CRUD 내부에서 commit 허용. Service 레이어 불필요, Router에서 직결 호출.

```python
# ❌ 잘못된 패턴 — CRUD에 비즈니스 규칙
async def create_profile(db, user_id, body):
    if await check_duplicate(...):   # 비즈니스 규칙 → Service 레이어로
        raise HTTPException(409)
    if not await has_any(...):       # 대표 자동설정 규칙 → Service 레이어로
        is_rep = True

# ✅ 올바른 패턴 — CRUD는 저장만
async def create_profile(db, user_id, birth_date, birth_time, is_representative, body):
    obj = Profile(...)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj          # commit 없음
```

### Service 작성 규칙

- 멀티스텝 흐름(검증 → 쓰기 → 재발급 등)을 제어하고 **마지막에 `await db.commit()` 한 번**.
- 예외 변환 책임: engine `ValueError` → `CalcFailedException`, LLM `RuntimeError` → `LLMFailedException`.
- OAuth 콜백처럼 `Request` 객체가 필요한 부분은 Router에 남기되, 추출한 **순수 데이터(email, social_id 등)** 만 Service로 전달.

```python
# ✅ 원자성 보장 패턴
async def exchange_refresh_token(db, raw_token):
    stored = await crud.get_active_refresh_token(db, hash_token(raw_token))  # 읽기
    stored.revoked = True                                                      # 마킹
    access, refresh = await crud.create_token_pair(db, user)                  # flush
    await db.commit()   # 폐기 + 신규 발급이 하나의 트랜잭션 ← 핵심
    return access, refresh
```

### Router 작성 규칙

- 엔드포인트 본문은 **의존성 주입 + 단일 위임 호출**로 끝낼 것.
- try/except 금지. 예외는 Service/CRUD가 `AppException` 서브클래스로 올리면 `main.py` 전역 핸들러가 처리.
- 단발 단순 연산은 Service 없이 CRUD 직결 허용 (불필요한 레이어 추가 금지).

```python
# ✅ 올바른 Router
@router.post("")
async def create_profile(body: ProfileCreate, user=Depends(...), db=Depends(...)):
    return await create_profile_for_user(db, user.id, body)  # 끝

# ❌ 잘못된 Router
@router.post("")
async def create_profile(...):
    try:
        dup = await db.execute(select(Profile).where(...))   # DB 직접
        if dup.scalar_one_or_none():
            raise HTTPException(409)                          # 비즈니스 로직
        ...
    except Exception as e:
        raise HTTPException(500)                              # 예외 변환
```

---

## 9. 구현 현황

### ✅ Phase 1 — 백엔드 엔진
- 12신살 (기둥별), 신살 18종, 공망, 득령/득지/득시/득세, 신강/신약 8단계
- 월운 API `GET /api/saju/wol-un`, 일진 달력 API `GET /api/saju/il-jin`
- 용신 표기 `yong_sin_label`

### ✅ Phase 2 — 프론트엔드 기반
- Nuxt.js 3, Tailwind CSS, Pinia, 입력 폼, API 클라이언트

### ✅ Phase 3 — 만세력 리포트 컴포넌트
- SajuTable, HapChungPanel, WuxingPentagram, WuxingDonutChart, SipseongDonutChart
- StrengthChart, YongSinBadge, DaeUnSlider, YeonUnSlider, WolUnSlider, IlJinCalendar

### ✅ Phase 4 — 인증·프로필·공유
- 구글 OAuth2 로그인
- 만세력 저장 (비로그인 시 localStorage 임시 보존 → 로그인 후 자동 저장)
- 내 만세력 목록 (`/my-profiles`) — 선택 → 실시간 재계산
- 결과 공유 — UUID 링크 → `/share/{uuid}` 비로그인 접근 가능

### ✅ Phase 4.5 — 오늘의 운세 + 한줄 상담
- 오늘의 운세: 명리 기반 6카테고리, AI 없음
- 한줄 상담: OpenAI GPT-4o 기반 단답형 상담, 공유/히스토리 페이지

### 🔜 Phase 5 — AI 탭 리포트 (Headline-Driven Insights)
- [ ] **Writer LLM 세팅** — `llm/providers.py` OpenAI GPT-4o 연결
- [ ] **프롬프트 작성** — calc 결과 + 고민 → 10개 결론형 헤드라인
- [ ] **PydanticOutputParser** — `ReportOutput(tabs: list[TabContent])` 스키마
- [ ] **사주 분석 파이프라인** — Engine → RAG → Context Filter → Writer
- [ ] **AI 리포트 탭 UI** — 헤드라인 탭 클릭 → 상세 내용 즉시 전환
- [ ] **궁합 파이프라인** — Synastry Engine → RAG → Writer

---

## 10. 핵심 계산 공식

- **진태양시 보정**: -30분 (동경 127° 보정)
- **연주 기준**: 1984년 = 갑자년, `(year-4)%10` = 천간, `(year-4)%12` = 지지
- **일주 기준일**: 1900-01-01 = 갑술일 (stemIdx=0, branchIdx=10)
- **월주 천간**: 갑·기년→병인월, 을·경년→무인월, 병·신년→경인월, 정·임년→임인월, 무·계년→갑인월
- **시주 천간**: `(일간index*2 + 시지index) % 10`
- **대운 공식**: 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세
- **24절기**: ephem 라이브러리 실시간 천문 계산
- **음력 변환**: korean-lunar-calendar 패키지

---

## 11. 프론트엔드 공통 컴포넌트

> **규칙**: 아래 컴포넌트가 이미 있다. 새 기능 추가 시 별도 지시 없이 반드시 가져다 써라. 중복 구현 금지.

### UI 범용 (`components/ui/`)

| 컴포넌트 | Props | 비고 |
|---|---|---|
| `<LoadingSpinner>` | `size?: 'sm'\|'md'\|'lg'` | 기본 md |
| `<UiShareModal>` | `v-model:show`, `url: string` | 열릴 때 자동 클립보드 복사, 하단 sheet + PC 중앙 |
| `<UiInfoTooltip>` | `text: string` | 호버/탭 토글, Teleport body |

### 앱 레벨 (`components/`)

| 컴포넌트 | Props / Slot | 비고 |
|---|---|---|
| `<AppDialog>` | `v-model:show`, `title`, `desc?`, `cancelText?` + default slot(액션 버튼) | Teleport body, 바깥 클릭 닫힘 |

### 사주 도메인 (`components/saju/`)

| 컴포넌트 | Props | 비고 |
|---|---|---|
| `<SajuInputForm>` | `submitLabel?`, emit `submit(SajuCalcRequest)` | 생년월일시·음양력·성별 입력 |
| `<SajuProfileList>` | `profiles`, `profLoad`, `loading?`, emit `select` | 저장된 만세력 목록, 일주·이미지 포함 |

### 애니메이션 규칙

- 페이지 진입 시 주요 섹션에 `animate-fade-up` 클래스 적용
- 순차 등장이 필요하면 `animate-delay-100` ~ `animate-delay-700` 조합
- `ClientOnly` 안 실제 콘텐츠에 `animate-fade-up` 래퍼를 씌워야 hydration 후 애니메이션 동작

### 로그인 유도 다이얼로그 표준 문구

| 상황 | title | desc |
|---|---|---|
| 저장된 만세력 접근 | `로그인이 필요해요` | `저장된 만세력은 로그인 후 이용할 수 있어요.` |
| 결과 저장 유도 | `매번 입력하기 번거로우시죠?` | `로그인하면 만세력을 저장해두고 바로 불러올 수 있어요.` |

### UI 용어 규칙

- 사용자에게 보이는 텍스트에서 **"프로필" → "만세력"** 으로 표기
  - 예: "저장된 만세력", "만세력 저장하기", "내 만세력"

---

## 11-1. 프론트엔드 아키텍처 패턴 (필수 준수)

### `useAsync()` — loading/error 보일러플레이트 금지

`loading = ref(false)` + `error = ref('')` + `try/catch/finally`를 직접 작성하지 않는다.
반드시 `useAsync()` composable을 사용한다.

```typescript
// ❌ 금지 — 직접 작성
loading.value = true
error.value   = ''
try {
  result.value = await api.getSomething()
} catch {
  error.value = '오류 메시지'
} finally {
  loading.value = false
}

// ✅ 올바른 패턴
const { loading, error, run } = useAsync()
const data = await run(() => api.getSomething(), '오류 메시지')
if (data) result.value = data
```

같은 페이지에서 독립적인 두 작업(예: 메인 계산 + 프로필 로드)이 있으면 각자 `useAsync()`를 별도로 생성한다:

```typescript
const { loading,              error, run: runCalc     } = useAsync()
const { loading: profLoad,          run: runProfiles  } = useAsync()
```

### `useSajuApi()` — API 호출 단일 창구

백엔드 API 호출은 항상 `useSajuApi()` composable을 통해 한다.
`$fetch`, `auth.authFetch`를 페이지/컴포넌트에서 직접 호출하지 않는다.

현재 제공 메서드:

| 메서드 | 설명 |
|---|---|
| `calcSaju(req)` | 만세력 계산 |
| `getWolUn(year, dayStem)` | 월운 |
| `getYeonUn(startYear, count, dayStem)` | 연운 |
| `getIlJin(year, month)` | 일진 |
| `getDailyFortune(req)` | 오늘의 운세 |
| `createDailyShare(birthInput)` | 오늘의 운세 공유 링크 생성 |
| `getDailyShareInput(token)` | 공유 운세 입력값 조회 |
| `askQuestion(req, authToken?)` | 한줄 상담 |
| `listConsultations(token)` | 상담 히스토리 목록 |
| `createConsultationShare(id, token?)` | 상담 공유 링크 생성 |
| `getSharedConsultation(shareToken)` | 공유 상담 조회 |
| `deleteConsultation(id, token)` | 상담 삭제 |
| `getProfiles(token)` | 저장된 만세력 목록 |
| `getRepresentativeProfile(token)` | 대표 만세력 조회 |

새로운 API 엔드포인트가 생기면 페이지가 아닌 `composables/useSajuApi.ts`에 추가한다.

### 타입·상수 단일 소스

중복 정의 금지. 아래 위치에만 존재한다:

| 항목 | 위치 |
|---|---|
| `ProfileResponse` | `types/saju.ts` |
| 한줄 상담 카테고리 레이블 | `utils/category.ts` → `QUESTION_CATEGORY_LABELS` |
| 오늘의 운세 카테고리 아이콘·순서 | `utils/category.ts` → `DAILY_CATEGORY_ICONS`, `DAILY_CATEGORY_ORDER` |
| 오행 → CSS 스와치 맵 | `utils/ganji.ts` → `EL_SWATCH` |
| 운세 점수 → 색상 | `utils/ganji.ts` → `scoreColor(score)` |
| 오늘 일주 계산 | `utils/ganji.ts` → `calcTodayIlju()` |
| 오늘 날짜 포맷 | `utils/ganji.ts` → `formatTodayLabel()` |

페이지나 컴포넌트에서 위 항목을 인라인으로 재정의하지 않는다.

### 에러 페이지

`frontend/error.vue` — Nuxt 전역 에러 페이지. 404/500 분기 처리.
새로 만들지 말고, 수정이 필요하면 이 파일을 수정한다.
