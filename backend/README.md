# Backend — FastAPI AI 파이프라인 서버

## 개요

사주팔자 계산 엔진, ChromaDB RAG, OpenAI LLM을 연결하는 FastAPI 서버입니다.

> "재물운" (X) → "30대 중반, 바위 틈에서 물이 솟구치듯 재물이 터질 팔자" (O)

---

## 실행

```bash
cd backend
cp .env.example .env
uv sync --group dev
uv run alembic upgrade head
uv run python -c "from rag.ingest import ingest_all; ingest_all()"   # 최초 1회
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | FastAPI |
| Pipeline | LangChain (LCEL) |
| LLM | OpenAI GPT-4o (기본) — Strategy Pattern (Gemini·Claude 교체 가능) |
| Output Parser | PydanticOutputParser + OutputFixingParser (langchain-core) |
| Vector DB | ChromaDB |
| Relational DB | PostgreSQL + SQLAlchemy 2.0 (async) |
| Auth | Google OAuth2 (authlib) + JWT (python-jose) |
| 도시 검색 | geonamescache + timezonefinder (완전 오프라인) |
| Package Manager | uv |

---

## 환경변수

| 변수 | 필수 | 기본값 | 설명 |
|---|---|---|---|
| `LLM_PROVIDER` | — | `openai` | LLM 선택 (`openai` \| `gemini` \| `claude`) |
| `OPENAI_API_KEY` | openai 시 필수 | — | OpenAI 플랫폼 발급 |
| `GEMINI_API_KEY` | gemini/embedding 시 필수 | — | Google AI Studio 발급 |
| `ANTHROPIC_API_KEY` | claude 시 필수 | — | Anthropic Console 발급 |
| `EMBEDDING_PROVIDER` | — | `openai` | 임베딩 제공사 |
| `CHROMA_PATH` | — | `./chroma_db` | ChromaDB 저장 경로 |
| `DATABASE_URL` | 필수 | — | `postgresql+asyncpg://user:pw@host:5432/db` |
| `GOOGLE_CLIENT_ID` | 필수 | — | Google OAuth2 클라이언트 ID |
| `GOOGLE_CLIENT_SECRET` | 필수 | — | Google OAuth2 시크릿 |
| `GOOGLE_REDIRECT_URI` | 필수 | — | OAuth 콜백 URI |
| `FRONTEND_URL` | 필수 | — | OAuth 완료 후 리다이렉트할 프론트엔드 주소 |
| `JWT_SECRET` | 필수 | — | JWT 서명 키 |

---

## 엔드포인트

| 메서드 | URL | 인증 | 기능 |
|---|---|---|---|
| GET | `/health` | — | 서버 상태 확인 |
| GET | `/api/auth/google` | — | Google OAuth2 로그인 시작 |
| GET | `/api/auth/google/callback` | — | OAuth2 콜백 처리 |
| POST | `/api/auth/refresh` | — | 액세스 토큰 갱신 |
| POST | `/api/auth/logout` | 필수 | 로그아웃 (refresh token 전체 폐기) |
| GET | `/api/auth/me` | 필수 | 현재 로그인 유저 정보 |
| POST | `/api/saju/calc` | — | 사주팔자 12단계 계산 |
| POST | `/api/saju/daily` | — | 오늘의 운세 (명리 기반) |
| GET | `/api/saju/wol-un` | — | 월운 조회 |
| GET | `/api/saju/il-jin` | — | 일진 달력 조회 |
| GET | `/api/saju/yeon-un` | — | 연운 조회 |
| POST | `/api/profiles` | 필수 | 만세력 저장 |
| GET | `/api/profiles` | 필수 | 내 만세력 목록 |
| GET | `/api/profiles/representative` | 필수 | 대표 만세력 조회 |
| PATCH | `/api/profiles/{id}/representative` | 필수 | 대표 만세력 설정 |
| GET | `/api/profiles/{id}` | 필수 | 만세력 단건 조회 |
| DELETE | `/api/profiles/{id}` | 필수 | 만세력 삭제 |
| POST | `/api/share` | 선택 | 만세력 결과 공유 링크 생성 |
| GET | `/api/share/{token}` | — | 공유된 만세력 결과 조회 |
| POST | `/api/share/daily` | — | 오늘의 운세 공유 링크 생성 |
| GET | `/api/share/daily/{token}` | — | 공유된 오늘의 운세 조회 |
| POST | `/api/question` | 선택 | 한줄 AI 상담 |
| GET | `/api/question/history` | 필수 | 상담 히스토리 (최근 50건) |
| POST | `/api/question/{id}/share` | 선택 | 상담 결과 공유 링크 생성 |
| DELETE | `/api/question/{id}` | 필수 | 상담 결과 삭제 |
| GET | `/api/question/share/{token}` | — | 공유된 상담 결과 조회 |
| GET | `/api/cities` | — | 도시 검색 |
| GET | `/docs` | — | Swagger UI |
| GET | `/redoc` | — | ReDoc |

---

## 인증 (Authentication)

Google OAuth2 Authorization Code Flow + JWT를 사용합니다. 액세스 토큰은 15분, 리프레시 토큰은 30일 유효하다. 액세스 토큰을 짧게 유지하면 탈취 시 피해 범위가 제한되고, 리프레시 토큰은 해시값만 DB에 저장하고 발급마다 갱신(rotation)하므로 탈취되어도 최초 사용 시점에 무효화된다. 세션 서버 없이도 로그아웃 시 `revoked=true`로 강제 폐기가 가능한 건 DB에 토큰 레코드가 있기 때문이다.

### 로그인 흐름

```
1. GET /api/auth/google
   → Google 로그인 페이지로 리다이렉트

2. GET /api/auth/google/callback?code=...
   → Google에서 액세스 토큰 교환
   → users 테이블에 계정 생성 또는 조회
   → JWT 액세스 토큰(15분) + 랜덤 리프레시 토큰(30일) 발급
   → 프론트엔드로 리다이렉트:
      {FRONTEND_URL}/auth/callback?access_token=JWT&refresh_token=TOKEN

3. POST /api/auth/refresh  {"refresh_token": "..."}
   → 새 액세스 토큰 + 리프레시 토큰 발급 (기존 토큰 폐기)

4. POST /api/auth/logout  (Authorization: Bearer <token>)
   → 해당 유저의 모든 리프레시 토큰 revoked=true
```

### 토큰 사용

```
Authorization: Bearer <access_token>
```

- 인증 필수 엔드포인트: 토큰 없으면 401
- 인증 선택 엔드포인트: 토큰 없어도 동작 (로그인 시 추가 기능 제공)

### 토큰 갱신 응답

```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "SomeBase64URLString...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## 표준 에러 응답

모든 에러는 아래 포맷으로 반환됩니다.

```json
{
  "timestamp": "2026-03-17T11:00:00Z",
  "path": "/api/saju/calc",
  "status": 422,
  "code": "VALIDATION_FAILED",
  "message": "입력값을 확인해 주세요.",
  "details": {
    "birth_date": "입력값: '1990/03/15' — 허용 형식: YYYY-MM-DD"
  }
}
```

### 에러 코드 목록

| HTTP | code | 설명 |
|---|---|---|
| 400 | `BAD_REQUEST` | 잘못된 요청 |
| 400 | `VALIDATION_FAILED` | 입력값 검증 실패 (field-level details 포함) |
| 400 | `INVALID_DATE_FORMAT` | 날짜 형식 오류 (허용 형식 안내) |
| 400 | `INVALID_BIRTH_YEAR` | 출생연도 범위 초과 (1900–2100) |
| 400 | `INVALID_QUERY_PARAM` | 쿼리 파라미터 오류 |
| 401 | `UNAUTHORIZED` | 인증 토큰 없음 또는 유효하지 않음 |
| 401 | `TOKEN_EXPIRED` | JWT 만료 |
| 401 | `OAUTH_FAILED` | Google OAuth 처리 실패 |
| 403 | `FORBIDDEN` | 리소스 접근 권한 없음 |
| 404 | `RESOURCE_NOT_FOUND` | 리소스를 찾을 수 없음 |
| 409 | `DUPLICATE_RESOURCE` | 동일한 프로필 이미 존재 |
| 422 | `CALC_FAILED` | 사주 계산 실패 |
| 429 | `TOO_MANY_REQUESTS` | 요청 한도 초과 |
| 500 | `INTERNAL_SERVER_ERROR` | 서버 내부 오류 |
| 500 | `DATABASE_ERROR` | DB 연결·쿼리 오류 |

---

## 로깅

### 액세스 로그

모든 요청에 대해 다음 형식으로 기록됩니다.

```
POST /api/saju/calc  status=200  time=1234ms  ip=127.0.0.1
```

- 미들웨어: `AccessLogMiddleware` (`middleware/logging.py`)
- 로거명: `sajubon.access`
- 측정: `time.perf_counter()` (마이크로초 정밀도)

### 애플리케이션 로그

```
2026-03-17T11:00:00 [INFO] sajubon — ...
```

- 레벨: INFO 이상
- 에러 발생 시 full traceback 기록 후 500 반환

---

## Engine 12단계 파이프라인

`calculate_saju()` 한 번 호출로 순차 실행됩니다. 각 단계의 출력이 다음 단계의 입력이라 병렬화 여지가 없다 — 격국(⑤)을 판단하려면 일간 강약(④)이 필요하고, 용신(⑥)은 격국 결과를 참조하며, 컨텍스트랭킹(⑪)은 격국·용신·신살을 모두 알아야 계산된다.

```
① 4기둥          연·월·일·시주 (진태양시 보정 포함)
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

계산 결과는 DB에 캐시하지 않는다. 사주 계산은 수십 ms 수준의 CPU 연산이라 LLM 호출(수 초)에 비하면 병목이 아니고, 캐시하면 엔진 로직이 바뀔 때 불일치 문제가 생긴다. 공유 링크만 예외로, 공유 시점 결과를 `calc_snapshot JSONB`로 저장한다 — 엔진이 개선되어도 공유된 링크는 당시 결과를 그대로 보여줘야 하기 때문이다.

### 핵심 계산 공식

| 항목 | 공식 | 비고 |
|---|---|---|
| 진태양시 보정 | 동경 127° 기준, 역사적 표준시 자동 적용 | 한국 표준시(UTC+9)는 실제 경도(127°)와 약 32분 차이 — 역사적 표준시 변경 이력도 반영 |
| 연주 기준 | 1984년 = 甲子년, `(year-4)%10` = 천간, `(year-4)%12` = 지지 | |
| 일주 기준일 | 1900-01-01 = 甲戌일 (stemIdx=0, branchIdx=10) | |
| 시주 천간 | `(일간index × 2 + 시지index) % 10` | |
| 대운 공식 | 3일=1년, 1일=4개월, 1시진(2h)=10일, 최대 10세 | |
| 24절기 | ephem 라이브러리 실시간 천문 계산 | TS 원본은 7200개 하드코딩 테이블 — 정확도·유지보수 문제로 실시간 계산으로 전환 |
| 음력 변환 | korean-lunar-calendar 패키지 | TS 원본은 300년치 테이블 — 패키지로 대체 |

---

## AI 파이프라인 (Phase 5 — 만세력 AI 탭 리포트)

LLM 한 번에 10개 탭을 모두 생성하면 앞쪽 탭에 맥락이 집중되고 뒤쪽 품질이 떨어지며, 헤드라인이 명리학적으로 타당한지 검증할 주체가 없다. 에이전트를 역할별로 분리해 각자 하나의 책임만 지게 한다. Planner와 Writer를 한 호출로 합치면 헤드라인 생성과 상세 작성이 서로 영향을 줘서 품질 관리 지점이 사라지기 때문에 Critic을 중간에 둔다.

```
Engine.calculate_saju()
  ↓
[Planner Agent]  — 사주 구조 + 고민 분석 → 10개 탭 헤드라인 초안 생성
  ↓
[Critic Agent]   — 헤드라인의 명리학적 타당성 점검, 중복·모순 탭 제거·수정
  ↓
[Writer Agent]   — 검증된 헤드라인 기반 RAG 검색 → 탭별 상세 내용 생성
  ↓
완성된 JSON (10탭) → Frontend
```

- **Planner**: 구조 분석에 집중, 문학적 표현 고려 없이 명리학 논거로 헤드라인 초안 작성
- **Critic**: Planner 출력 검토, "이 탭이 이 사주에 실제로 해당하는가" 검증, 유사 탭 통합
- **Writer**: Critic이 승인한 헤드라인으로 RAG 지식을 조합해 최종 문장 생성

---

## 한줄 상담 파이프라인 (`POST /api/question`)

Guard가 첫 번째 LLM 호출로 차단 여부와 카테고리를 동시에 판단한다. 차단 케이스는 후속 파이프라인이 실행되지 않아 불필요한 사주 계산·RAG 검색·Writer 비용이 발생하지 않는다.

```
1. Guard + Category 분류  (LLM 1-call)
   ├─ BLOCKED   → 경고 문구 즉시 반환 (성적·폭력·범죄·명예훼손)
   ├─ MEDICAL   → 의료 면책 문구 프롬프트에 추가
   ├─ INSTANT   → 사주 계산 없이 즉답 (불가능한 전제·즉각적 물리 요구)
   └─ OK        → career / love / money / health / general 자동 분류

2. 사주 계산  (handle_calculate_saju)
   → 일간·일지·용신·대운 등 12단계 결과

3. RAG 검색 + 재순위
   → ten_gods / sin_sal / structure_patterns / ilju 컬렉션 각 3개
   → ChromaDB 거리 점수에 용신 오행 부스트·기신 오행 패널티·카테고리 태그 보너스 적용
     (시맨틱 유사도만으론 "이 사람에게 의미 있는 청크"를 구분할 수 없어서)
   → 상위 4개 청크 선택
   → timing 카테고리(love/career/money): 세운·월운 추가 포함

4. Writer LLM  (OpenAI GPT-4o)
   → 사주 계산 결과 + RAG 지식 + 고민
   → ConsultationOutput(headline, content)

5. DB 저장  (consultations 테이블)
   → user_id (로그인 시), birth_input, question, category, headline, content
```

**요청 예시:**
```json
{
  "name": "홍길동",
  "birth_date": "1990-03-15",
  "birth_time": "14:30",
  "gender": "male",
  "calendar": "solar",
  "question": "올해 이직 운이 있을까요?"
}
```

**응답 예시:**
```json
{
  "id": 42,
  "headline": "변화의 파도가 이미 당신 발아래까지 왔습니다",
  "content": "정관격에 식상운이 들어온 지금...",
  "category": "career"
}
```

---

## LLM Strategy Pattern

`LLM_PROVIDER` 환경변수 하나로 전체 파이프라인의 모델을 교체할 수 있다. OpenAI GPT-4o는 한국어 표현력이 높지만 비용이 크고, 짧은 출력이면 Gemini Flash로 충분하거나 향후 온프레미스 전환이 필요할 수 있어 코드 변경 없이 전환 가능하게 설계했다. 파싱 실패 시 `OutputFixingParser`가 JSON을 수정해 자동 재시도하므로 LLM이 유효하지 않은 JSON을 반환해도 서비스 오류로 이어지지 않는다.

```
.env: LLM_PROVIDER=openai (기본) | gemini | claude

지원 모델
  openai → gpt-4o
  gemini → gemini-2.0-flash
  claude → claude-sonnet-4-6
```

---

## RAG 지식 베이스 (ChromaDB)

| 컬렉션 | 문서 수 | 내용 |
|---|---|---|
| `ilju` | 60 | 60갑자 일주론 (아키타입·직업·연애·취약점) |
| `ten_gods` | 10 | 십성 해석 (비견~정인) |
| `sin_sal` | 가변 | 신살 의미 (역마·도화·귀문관살 등) |
| `structure_patterns` | 가변 | 구조 패턴 15종 해석 |
| `dynamics` | 가변 | 동역학 (천간합·충·삼합) 해석 |
| `wuxing` | 가변 | 오행 상생·상극 해석 |

`ten_gods`, `sin_sal`, `structure_patterns`은 고민 문장을 임베딩해 유사 청크를 반환하는 시맨틱 검색을 사용한다. `ilju`는 다르다 — "경오"면 `ilju == "경오"` 문서를 통째로 꺼내서 Writer에게 넘긴다. 일주 문서는 성격·직업·연애·취약점·상담 스크립트까지 담긴 메인 레퍼런스로, 탭 전 구간에서 참조된다. 벡터 검색으로 "유사한" 일주를 반환하는 건 의미가 없다 — 이 사람의 일주가 "경오"면 정확히 경오 문서가 필요하다.

### ilju 문서 구조

```
ilju 문서
│
├── embedding_context         ChromaDB 인덱싱용 1~2문장 맥락 요약
│                             인덱싱 텍스트와 Writer 참조 JSON을 분리해 임베딩 품질을 제어
│
├── core_keywords             Writer 프롬프트에 직접 주입하는 간지·구조 키워드 배열
│                             ("壬子", "수기극집중", "감정억제경향")
│                             LLM이 이 키워드로 간지 수준 정확도의 헤드라인을 생성
│
├── psychological_traits      영문 스네이크 케이스 — 임베딩 문서에 포함
│   (vs)                      "내향적이고 분석적인 사람" 쿼리에 매칭되도록
├── tags                      한글 복합어 — Writer가 직접 읽는 창의적 표현 힌트
│                             ("심해의지혜", "밤의전문가") — 문학적 표현의 씨앗
│
├── energy_profile            오행 구조를 기계 가독성 있는 구조체로 표현
│                             Writer가 용신 결과와 교차해 "용신이 일주 흐름과 자연스럽게 연결"
│                             같은 맥락을 만들 수 있도록
│
├── variance_note             같은 일주여도 월지·용신에 따라 발현이 달라지는 분기 힌트
│                             ("주변 오행에 따라 냉철한 전략가 / 고독한 예술가로 변용")
│                             Writer가 사람마다 다른 결론을 쓸 수 있게 하는 가이드
│
├── compatibility             harmonious / conflict 목록에 ilju·reason·tag 포함
│                             궁합 파이프라인에서 두 사람 일주 문서를 꺼내면
│                             별도 엔진 계산 없이 합충 관계 방향성을 즉시 파악 가능
│
└── consulting_points
    ├── empathy_trigger       고민 상담 탭 도입부용 공감 문장
    ├── solution_speech       조언 파트용 명리학적 처방 문장
    └── tab_headline          사전 검증된 결론형 헤드라인
                              LLM이 완전 창작하면 퀄리티 편차가 커서
                              명리학적으로 검토된 헤드라인을 데이터 레벨에 심어두고
                              Writer가 참고·변형하게 함
```

```bash
# 최초 실행 또는 knowledge JSON 변경 시 재인덱싱
uv run python -c "from rag.ingest import ingest_all; ingest_all()"
```

---

## 모듈 구조

```
backend/
├── main.py                         # FastAPI 앱 진입점, 미들웨어, 라우터 등록
├── pyproject.toml
├── .env.example
│
├── engine/                         # 만세력 계산 엔진
│   ├── calc/                       # 순수 계산 모듈 — 외부 의존성 없음, 단위 테스트 용이
│   │   ├── saju.py                 # 4기둥 계산
│   │   ├── ten_gods.py             # 십성·12운성
│   │   ├── sin_sal.py              # 신살 (18종)
│   │   ├── day_master_strength.py  # 일간 강약 8단계 + 득령/득지/득시/득세
│   │   ├── gyeok_guk.py            # 격국 (13종)
│   │   ├── yong_sin.py             # 용신 (억부/조후/통관)
│   │   ├── dae_un.py               # 대운
│   │   ├── daily_fortune.py        # 오늘의 운세 (명리 기반 6카테고리, LLM 없음)
│   │   ├── solar_terms.py          # 24절기 (ephem 실시간 계산)
│   │   ├── calendar_converter.py   # 음양력 변환
│   │   └── validation.py           # 입력값 검증
│   ├── analysis/                   # calc 결과 → RAG·LLM이 소비하기 좋은 형태로 후처리
│   │   ├── structure_patterns.py   # calc 로직과 분리해 RAG 전략 변경 시 calc 무관
│   │   ├── dynamics.py
│   │   ├── synergy.py
│   │   ├── behavior_synthesizer.py
│   │   ├── context_ranker.py
│   │   └── life_domain_mapper.py
│   └── data/                       # 정적 명리학 데이터 (Python dict)
│       ├── heavenly_stems.py
│       ├── earthly_branches.py
│       ├── wuxing.py
│       └── timezone_history.py
│
├── rag/                            # ChromaDB 명리 지식 검색
│   ├── db.py
│   ├── ingest.py
│   ├── search.py
│   ├── providers.py                # Embedding Strategy Pattern
│   └── knowledge/                  # 명리학 지식 JSON (105개 문서)
│
├── llm/                            # Writer LLM
│   ├── providers.py                # LLM Strategy Pattern
│   └── pipelines/
│       └── question.py             # 한줄 상담 파이프라인
│
├── routers/                        # FastAPI 라우터
│   ├── auth.py                     # /api/auth
│   ├── saju.py                     # /api/saju
│   ├── question.py                 # /api/question
│   ├── profiles.py                 # /api/profiles
│   ├── share.py                    # /api/share
│   └── cities.py                   # /api/cities
│
├── schemas/                        # Pydantic v2 스키마
│   ├── saju.py                     # SajuCalcRequest / SajuCalcResponse
│   ├── daily.py                    # DailyFortuneRequest / DailyFortuneResponse
│   ├── profile.py                  # ProfileCreate / ProfileResponse
│   ├── question.py                 # QuestionRequest / QuestionResponse / ConsultationDetail
│   ├── share.py                    # ShareCreate / ShareResponse / SharedResultResponse
│   └── report.py                   # (Phase 5) SajuReportRequest / SajuReportResponse
│
├── db/
│   ├── models.py                   # User, Profile, RefreshToken, DailyShare, SharedResult, Consultation
│   └── session.py                  # async 세션 팩토리
│
├── core/
│   ├── config.py                   # pydantic-settings 환경변수
│   ├── errors.py                   # ErrorCode enum
│   └── exceptions.py               # AppException 및 하위 예외 클래스
│
├── middleware/
│   └── logging.py                  # AccessLogMiddleware
│
└── dependencies/
    ├── auth.py                     # get_current_user / get_optional_user
    └── db.py                       # get_db
```

---

## 아키텍처 설계 결정

### Router → Service → CRUD 3계층

라우터가 DB 쿼리를 직접 작성하고 LLM을 직접 호출하면, 한 파일에 HTTP 입출력·비즈니스 흐름·영속성 로직이 섞여 어느 계층의 문제인지 추적이 어렵다. 이를 세 계층으로 분리했다.

| 계층 | 디렉토리 | 책임 |
|---|---|---|
| **Router** | `routers/` | HTTP 입출력, 인증 의존성 주입. try/except 없음 — 예외는 위로 전파 |
| **Service** | `services/` | 비즈니스 흐름 조율 (엔진 호출 → 데이터 가공 → CRUD 위임). 예외 변환 담당 |
| **CRUD** | `crud/` | DB 접근 전용. `select`, `db.add`, `db.commit`이 여기에만 존재 |

라우터 엔드포인트가 서비스 함수 한 줄 호출로 끝나는 게 목표다. `routers/saju.py`의 6개 엔드포인트가 각각 1줄인 게 그 결과다.

### CRUD 패턴 vs 레포지토리 패턴

이 프로젝트는 정석 레포지토리 패턴(Repository Pattern)을 쓰지 않는다. 두 방식의 차이는 **추상화의 정도**다.

레포지토리 패턴의 본질은 "비즈니스 로직이 데이터 저장소가 무엇인지 모르게 한다"는 것이다. `class UserRepository`가 인터페이스를 정의하면 구현체가 PostgreSQL일 수도, 인메모리일 수도 있다 — DB를 교체해도 서비스 코드는 손대지 않아도 된다. 대신 추상 클래스·인터페이스·구현체 3단계가 생겨 코드량이 늘고, 실제 교체가 일어나지 않는 프로젝트에서는 오버 엔지니어링이 된다.

이 프로젝트에서 PostgreSQL을 다른 DB로 바꿀 가능성은 거의 없다. 그래서 `crud/consultation.py` 안에 SQLAlchemy 문법이 직접 들어있다 — SQL 엔진에 의존하지만 의도적인 선택이다. 함수 단위 CRUD는 코드 중복을 제거하고 라우터 비대화를 막는다는 레포지토리 패턴의 실용적 목적은 달성하면서, Java식 인터페이스 계층 없이 파이썬스럽게 유지한다.

FastAPI의 `Depends()` 기반 의존성 주입은 클래스 없이도 테스트에서 CRUD 함수를 그대로 교체할 수 있어, 정식 레포지토리 패턴 없이도 테스트 격리가 가능하다.

### 예외 처리 흐름

서비스가 예외를 `AppException` 서브클래스로 변환하고, 전역 핸들러(`main.py`)가 이를 HTTP 응답으로 변환한다. 라우터는 예외를 잡지 않는다.

```
engine / LLM  →  raw exception (ValueError, RuntimeError, ...)
      ↓
  service     →  AppException 서브클래스로 변환
                  ValueError (날짜)  →  InvalidDateFormatException  400
                  ValueError (기타)  →  CalcFailedException         422
                  RuntimeError       →  LLMFailedException          500  ← LLM 파싱 실패
                  AppException       →  그대로 통과 (이중 변환 방지)
      ↓
  router      →  아무것도 하지 않음
      ↓
  main.py     →  전역 AppException 핸들러 → ErrorResponse JSON 반환
```

`services/saju.py`의 `_calc_guard()` 컨텍스트 매니저가 이 변환을 한 곳에서 담당한다. 엔진 핸들러를 직접 호출하는 6개 서비스 함수 모두 `with _calc_guard():` 한 줄로 동일한 예외 처리 정책을 적용한다.

---

## DB 스키마

### 테이블 목록

| 테이블 | 설명 |
|---|---|
| `users` | 계정 (email, provider, social_id, role) |
| `profiles` | 만세력 입력값 (birth_date, birth_time, calendar, gender 등) |
| `refresh_tokens` | JWT 리프레시 토큰 (token_hash, expires_at, revoked) |
| `shared_results` | 만세력 결과 공유 스냅샷 (calc_snapshot JSONB) |
| `daily_shares` | 오늘의 운세 공유 (birth_input JSONB, 접근 시 재계산) |
| `consultations` | 한줄 상담 결과 (question, headline, content, share_token) |

`profiles`에는 입력값(생년월일시·성별·음양력)만 저장하고 계산 결과는 저장하지 않는다. 엔진이 개선될 때 과거 프로필도 자동으로 최신 결과를 얻기 위해서다. `shared_results`는 예외로, 공유 시점 결과를 `calc_snapshot JSONB`로 저장한다 — 나중에 엔진이 바뀌어도 공유된 링크는 당시 결과를 그대로 보여줘야 하기 때문이다.

### 마이그레이션 이력

```
0001  init: users, profiles, refresh_tokens, shared_results
0002  profiles: is_representative 컬럼 추가
0003  profiles: day_stem, day_branch 컬럼 추가 (이후 제거)
0004  daily_shares 테이블 추가
0005  consultations 테이블 추가
0006  profiles: day_stem/day_branch 제거 (응답 시 동적 계산으로 전환)
```

0006에서 `day_stem`/`day_branch`를 제거한 이유: 초기에는 프로필 목록 UI의 일주 표시를 위해 DB에 저장했으나, 엔진 결과와 저장값 불일치 문제와 동적 계산이 충분히 빠르다는 확인 이후 제거했다.

---

## 도시 검색 API

### `GET /api/cities?q=검색어`

geonamescache(150k+ 도시) + timezonefinder를 이용한 완전 오프라인 도시 검색. 외부 Geocoding API(Google Maps 등) 없이 운영하기 위해 오프라인 방식을 선택했다. 도시를 선택하면 진태양시 보정에 필요한 경도·타임존이 함께 반환된다.

```bash
curl "http://localhost:8000/api/cities?q=서울"
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

## 사용된 오픈소스 라이브러리

| 패키지 | 버전 | 라이선스 | 용도 |
|---|---|---|---|
| [FastAPI](https://github.com/tiangolo/fastapi) | ≥0.111 | MIT | REST API 프레임워크 |
| [uvicorn](https://github.com/encode/uvicorn) | ≥0.29 | BSD-3-Clause | ASGI 서버 |
| [Pydantic](https://github.com/pydantic/pydantic) | ≥2.0 | MIT | 데이터 모델·입력 검증 |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | ≥2.0 | MIT | 환경변수 설정 관리 |
| [LangChain](https://github.com/langchain-ai/langchain) | ≥0.2 | MIT | LLM 파이프라인 (LCEL) |
| [langchain-openai](https://github.com/langchain-ai/langchain-openai) | ≥0.1 | MIT | OpenAI LLM 연동 |
| [langchain-google-genai](https://github.com/langchain-ai/langchain-google-genai) | ≥1.0 | MIT | Gemini LLM 연동 |
| [langchain-anthropic](https://github.com/langchain-ai/langchain-anthropic) | ≥0.1 | MIT | Claude LLM 연동 |
| [ChromaDB](https://github.com/chroma-core/chroma) | ≥0.5 | Apache-2.0 | 벡터 DB |
| [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) | ≥2.0 | MIT | 비동기 ORM |
| [asyncpg](https://github.com/MagicStack/asyncpg) | ≥0.29 | Apache-2.0 | PostgreSQL 비동기 드라이버 |
| [Alembic](https://github.com/sqlalchemy/alembic) | ≥1.13 | MIT | DB 마이그레이션 |
| [authlib](https://github.com/lepture/authlib) | ≥1.3 | BSD-3-Clause | Google OAuth2 클라이언트 |
| [python-jose](https://github.com/mpdavis/python-jose) | ≥3.5 | MIT | JWT 생성·검증 |
| [itsdangerous](https://github.com/pallets/itsdangerous) | ≥2.1 | BSD-3-Clause | 세션 서명 (CSRF) |
| [httpx](https://github.com/encode/httpx) | ≥0.28 | BSD-3-Clause | 비동기 HTTP 클라이언트 |
| [ephem](https://github.com/brandon-rhodes/pyephem) | ≥4.1 | MIT | 24절기 천문 계산 |
| [korean-lunar-calendar](https://github.com/usingsky/korean_lunar_calendar_py) | ≥0.3.1 | MIT | 음력 ↔ 양력 변환 |
| [pytz](https://github.com/stub42/pytz) | ≥2024.1 | MIT | 표준시·시간대 처리 |
| [geonamescache](https://github.com/yaph/geonamescache) | ≥1.4 | MIT | 도시 데이터베이스 |
| [timezonefinder](https://github.com/jannikmi/timezonefinder) | ≥6.5 | MIT | 좌표 → IANA 타임존 변환 |
| [pytest](https://github.com/pytest-dev/pytest) | ≥8.0 | MIT | 단위 테스트 |
| [uv](https://github.com/astral-sh/uv) | — | MIT / Apache-2.0 | Python 패키지 매니저 |
