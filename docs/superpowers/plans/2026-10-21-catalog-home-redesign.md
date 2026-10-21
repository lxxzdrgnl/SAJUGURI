# 디자인 시스템 개편 + 진열대 홈 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 브루탈 디자인을 걷어낸 새 라이트/다크 디자인 시스템을 깔고, 메인을 오늘의 운세 중심 상품 진열대로 바꾸며, 하단 탭을 ≡ 드로어로 대체한다.

**Architecture:** 의미 기반 색 토큰(라이트·다크 값)을 `packages/design`에 추가하고 웹은 CSS 변수로 소비한다. 상품 정의·검색·큐레이션은 플랫폼 무관 TS로 `packages/core`에 두고, 상품 이름·문구는 next-intl 메시지에 둔다. 홈은 서버 컴포넌트가 `?cat=` 로 전체 큐레이션/카테고리 그리드를 분기하고, 상품 열람은 백엔드 `product_views` 테이블에 fire-and-forget으로 기록한다.

**Tech Stack:** Next.js 15 App Router · next-intl 4 · Tailwind v4 (`@theme inline`) · vitest · FastAPI + SQLAlchemy async + alembic · pytest · OpenAI gpt-image-1 (일러스트 스크립트)

**Spec:** `docs/superpowers/specs/2026-10-21-catalog-home-redesign-design.md`

## Global Constraints

- 모바일 단일 컬럼 max-width 640px 가운데 정렬, PC 전용 레이아웃 금지, 가로 스크롤 금지.
- 색은 토큰만 사용 — 컴포넌트에 임의 HEX 금지 (G2). UI 이모지 금지, 스트로크 SVG 아이콘(24 viewBox, stroke-width 2, round cap/join).
- 브루탈(굵은 잉크 테두리 + 오프셋 그림자) 신규 사용 금지. 새 화면은 `Card`/`Button`만.
- 포인트 컬러 옐로 `#FFD900` 유지.
- `apps/web` UI 문자열 하드코딩 금지 — `messages/ko.json`·`en.json` 동시 작성, `node apps/web/scripts/check-i18n.mjs` 통과.
- `packages/`에 브라우저 API(window·document·localStorage·EventSource) 직접 호출 금지 (G1).
- `packages/design`의 기존 export(`colors`, `shadow.brutal` 등)는 삭제·변경 금지 — `apps/mobile`이 쓴다. 새 토큰은 옆에 추가.
- 오늘의 운세 스토리(`components/fortune/FortuneStoryPage.tsx`, `StoryCard.tsx`, `SummaryCard.tsx`) 수정 금지.
- 다크 모드 선택 UI는 Task 20 전까지 노출 금지 — 그때까지 라이트 고정.
- 큐레이션 동안 "많이 본" 문구 금지 — 선반 제목 "○○ 일간에게 추천", 랭킹 제목 "구리구리 추천".
- `frontend/`(Nuxt) 수정 금지.
- 커밋: `<type>: <한 줄 요약>`, scope 괄호 금지, **Co-Authored-By 금지** (AGENTS.md G6), 독립 변경은 분리.
- 배포: Task 1~11 = 1차 배포 묶음(탭 바 제거와 드로어는 반드시 같은 배포). Task 12 이후는 태스크 단위로 배포 가능.

## Review Focus

- 로그인했지만 만세력이 0개이거나 대표가 없는 사용자 → 헤더는 "내 일간 찾기", 선반은 "요즘 많이 보는" 대신 인기 큐레이션(`popular`)으로 정상 표시. (Task 3 테스트)
- 캐시된 운세가 깨졌거나 overall 카드가 없는 스토리 → 히어로가 "안 본 날" 상태로 떨어지고 크래시하지 않음. (Task 8 테스트)
- 검색어에 공백·대소문자·영어 로케일·매칭 없음 → 정규화해서 매칭, 없으면 빈 배열 + "구리구리한테 상담하기" 폴백. (Task 3 테스트)
- 열람 기록 API에 잘못된 product_id·게스트 요청·네트워크 실패 → 422/204로 응답하고 화면 동작에는 영향 없음. (Task 4·5 테스트)
- 긴 이름(10자 한글)·영어 로케일 긴 상품명 → 헤더 칩·포스터 제목이 말줄임/줄바꿈되고 360px 폭에서 가로 스크롤 없음. (Task 7·9 확인 단계)

---

## 1차 배포 묶음 (Task 1~11)

### Task 1: 의미 기반 색 토큰 (라이트·다크)

**Files:**
- Modify: `packages/design/src/tokens.ts` (파일 끝에 추가)
- Modify: `packages/design/src/index.ts` (새 export 노출 확인)
- Test: `packages/design/src/tokens.test.ts`

**Interfaces:**
- Produces:
  ```ts
  export type ThemeName = 'light' | 'dark'
  export interface SemanticColors {
    bg: string; surface: string; surfaceSoft: string; line: string
    text: string; textSub: string; accent: string; onAccent: string
    danger: string; counselBg: string; counselFg: string
  }
  export const semantic: Record<ThemeName, SemanticColors>
  export const ohaengByTheme: Record<ThemeName, Record<'목'|'화'|'토'|'금'|'수', string>>
  export const ohaengTintByTheme: Record<ThemeName, Record<'목'|'화'|'토'|'금'|'수', string>>
  ```

- [ ] **Step 1: Write the failing test** — `tokens.test.ts`에 추가:
  - `semantic.light`와 `semantic.dark`가 같은 키 집합을 가진다.
  - `semantic.light.accent === '#FFD900'` 이고 `semantic.dark.accent === '#FFD900'`.
  - 모든 값이 `/^#[0-9A-F]{6}$/i`.
  - 각 테마에서 `text` 대 `bg` 대비비 ≥ 7, `textSub` 대 `bg` ≥ 4.5, 각 오행색 대 `bg` ≥ 3 (테스트 안에 WCAG 상대휘도 대비 헬퍼 작성).
  - 기존 `colors.bgBase`·`shadow` export가 여전히 존재한다 (모바일 보호).
- [ ] **Step 2: Run** `pnpm --filter @sajuguri/design test` → FAIL (`semantic` 없음)
- [ ] **Step 3: Implement** `semantic`, `ohaengByTheme`, `ohaengTintByTheme` in `tokens.ts`. 라이트: bg `#FFFFFF`, surfaceSoft 크림 계열, line 연한 웜그레이. 다크: bg `#121212` 근처, surface `#1A1A1A` 근처. `counselBg`는 두 테마 모두 `#04332F`, `counselFg` `#E9F4F1`. 나머지 값은 대비 테스트를 통과하는 범위에서 결정.
- [ ] **Step 4: Run** `pnpm --filter @sajuguri/design test` → PASS, `pnpm --filter mobile typecheck` → PASS
- [ ] **Step 5: Commit** `feat: 라이트·다크 의미 기반 색 토큰 추가`

### Task 2: 웹 토큰 레이어 + Card·Button 컴포넌트

**Files:**
- Modify: `apps/web/app/globals.css` (새 변수 블록 추가, 기존 변수·브루탈 유틸은 유지)
- Create: `apps/web/components/ui/Card.tsx`, `apps/web/components/ui/Button.tsx`
- Modify: `apps/web/app/[locale]/layout.tsx` (디스플레이 글꼴 변수 자리)

**Interfaces:**
- Consumes: Task 1 `semantic` 값 (CSS에 같은 HEX를 옮겨 적는다 — 기존 globals.css가 packages/design을 손으로 미러링하는 방식 그대로)
- Produces:
  - CSS 변수 `--c-bg --c-surface --c-surface-soft --c-line --c-text --c-text-sub --c-accent --c-on-accent --c-danger --c-counsel-bg --c-counsel-fg` (라이트 값은 `:root`, 다크 값은 `:root[data-theme="dark"]` — Task 20 전까지 data-theme을 아무도 설정하지 않으므로 라이트 고정)
  - Tailwind 색 `bg-c-bg`, `text-c-text`, `border-c-line` … (`@theme inline`에 `--color-c-*` 매핑)
  - `--font-display` (지금은 `var(--font-sans)`의 굵은 폴백, Task 11에서 실제 글꼴로 교체)
  - 반경 토큰은 기존 `--radius-*` 유지, 새 카드용 `--radius-card: 20px`, `--radius-pill: 999px`
  - `Card({ tone = 'plain', className, children }: { tone?: 'plain' | 'soft' | 'counsel'; className?: string; children: ReactNode })` — plain=surface+1px line, soft=surfaceSoft 무테, counsel=counselBg/counselFg. 그림자 없음.
  - `Button({ variant = 'primary', size = 'md', className, ...rest }: ButtonHTMLAttributes & { variant?: 'primary' | 'secondary' | 'ghost'; size?: 'sm' | 'md' })` — primary=accent 배경+onAccent, secondary=surface+line, ghost=투명. pill 반경. `Link`로 쓸 때를 위해 같은 클래스를 내보내는 `buttonClass(variant, size): string`도 export.

- [ ] **Step 1: Add CSS 변수·@theme 매핑** — `body` 배경은 아직 `--bg-base` 유지(옛 화면 보호). 새 화면은 래퍼에서 `bg-c-bg`를 직접 쓴다.
- [ ] **Step 2: Create `Card.tsx`, `Button.tsx`** — 위 시그니처, 포커스 링은 기존 `:focus-visible` 규칙 재사용, 눌림 피드백은 `active:scale-[0.98]` + `transition-transform` (`--motion-duration-press`).
- [ ] **Step 3: Run** `pnpm --filter web typecheck` → PASS, `pnpm --filter web build` → 성공
- [ ] **Step 4: Commit** `feat: 새 디자인 토큰 레이어와 Card·Button 컴포넌트`

### Task 3: 상품 카탈로그·검색·큐레이션 (packages/core)

**Files:**
- Create: `packages/core/src/catalog/products.ts`, `packages/core/src/catalog/search.ts`, `packages/core/src/catalog/curation.ts`, `packages/core/src/catalog/ageBand.ts`
- Modify: `packages/core/src/index.ts` (export)
- Test: `packages/core/src/catalog/products.test.ts`, `search.test.ts`, `curation.test.ts`, `ageBand.test.ts`

**Interfaces:**
- Produces:
  ```ts
  export type ProductId = 'daily_fortune' | 'guriguri_counsel' | 'saju_report' | 'compatibility'
    | 'question' | 'some_heart' | 'reunion' | 'career_move' | 'money_flow'
  export type ProductCategory = 'fortune' | 'love' | 'reunion' | 'compat' | 'career' | 'money'
  export const CATEGORY_ORDER: readonly ProductCategory[]   // 탭 순서: fortune, love, reunion, compat, career, money
  export interface Product {
    id: ProductId
    categories: ProductCategory[]
    status: 'available' | 'coming_soon'
    href: string | null          // available만, 로케일 프리픽스 없는 앱 경로
    art: string                  // 공개 경로 (/mascot/... 또는 /products/<id>.png)
    keywords: { ko: string[]; en: string[] }
  }
  export const PRODUCTS: readonly Product[]
  export function getProduct(id: ProductId): Product
  export function productsInCategory(cat: ProductCategory): Product[]
  export function searchProducts(query: string, locale: 'ko' | 'en'): Product[]
  export type Element = '목' | '화' | '토' | '금' | '수'
  export interface Shelf { kind: 'ilgan' | 'popular'; productIds: ProductId[] }
  export function curatedShelf(dayStem: string | null): Shelf
  export function curatedRanking(): ProductId[]
  export const SITUATIONS: readonly { key: 'some' | 'breakup' | 'quit' | 'money'; productId: ProductId }[]
  export function ageBand(birthDate: string, today: Date): string | null   // '25-29' 형식
  ```
- 상품 고정값:
  | id | categories | status | href | art(임시) |
  |---|---|---|---|---|
  | daily_fortune | fortune | available | `/fortune` | `/mascot/fortune.png` |
  | guriguri_counsel | love, career, money | available | `/chat` | `/mascot/thumbsup.png` |
  | saju_report | fortune | available | `/report/new` | `/mascot/calendar.png` |
  | compatibility | compat, love | available | `/compatibility/new` | `/mascot/love.png` |
  | question | fortune | available | `/question` | `/mascot/cookie.png` |
  | some_heart | love | coming_soon | null | `/mascot/love.png` |
  | reunion | reunion, love | coming_soon | null | `/mascot/love.png` |
  | career_move | career | coming_soon | null | `/mascot/calendar.png` |
  | money_flow | money | coming_soon | null | `/mascot/cookie.png` |
- SITUATIONS: some→some_heart, breakup→reunion, quit→career_move, money→money_flow.
- curatedShelf: 일간 천간→오행(갑을=목, 병정=화, 무기=토, 경신=금, 임계=수)별 3~4개 목록을 상수로 둔다(목록 구성은 재량, 각 목록에 coming_soon 1개 이상 포함). `null`·알 수 없는 천간 → `{ kind: 'popular', productIds: [...] }`.
- curatedRanking: `['daily_fortune', 'compatibility', 'saju_report']`.

- [ ] **Step 1: Write the failing tests**
  - products: `PRODUCTS` id 중복 없음; `status==='available'` ⇔ `href !== null`; 모든 상품 `keywords.ko`·`keywords.en` 각 1개 이상; `productsInCategory('love')`에 `some_heart`, `reunion`, `compatibility`, `guriguri_counsel` 포함.
  - search: `searchProducts('재회', 'ko')[0].id === 'reunion'`; `searchProducts('  이 직 ', 'ko')`에 `career_move` 포함(공백 제거 정규화); `searchProducts('REUNION', 'en')[0].id === 'reunion'`(대소문자 무시); `searchProducts('', 'ko')` → `[]`; `searchProducts('ㅋㅋㅋ없는말', 'ko')` → `[]`.
  - curation: `curatedShelf('임').kind === 'ilgan'`이고 길이 3~4; `curatedShelf(null).kind === 'popular'`; `curatedShelf('X').kind === 'popular'`; 모든 productIds가 `PRODUCTS`에 존재; `curatedRanking()` 위 값과 동일.
  - ageBand: `ageBand('2001-08-17', new Date('2026-10-21')) === '25-29'`; `ageBand('2010-01-01', new Date('2026-10-21')) === '15-19'`; 미래 날짜 → `null`; `'not-a-date'` → `null`.
- [ ] **Step 2: Run** `pnpm --filter @sajuguri/core test` → FAIL
- [ ] **Step 3: Implement** — search 정규화: `trim` → 소문자 → 공백 제거; 매칭은 키워드(정규화)가 쿼리를 포함하거나 쿼리가 키워드를 포함; 결과는 일치 키워드가 쿼리와 완전 일치하는 상품 먼저. ageBand는 만 나이를 5년 구간 하한으로 내림.
- [ ] **Step 4: Run** `pnpm --filter @sajuguri/core test` → PASS
- [ ] **Step 5: Commit** `feat: 상품 카탈로그·검색·큐레이션 정의`

### Task 4: 상품 열람 기록 백엔드

**Files:**
- Modify: `backend/db/models.py` (끝에 `ProductView`)
- Create: `backend/alembic/versions/0018_add_product_views.py` (revision `"0018"`, down_revision `"0017"`)
- Create: `backend/crud/product_views.py`, `backend/schemas/product_views.py`, `backend/routers/product_views.py`
- Modify: `backend/main.py` (`app.include_router(product_views.router)`)
- Test: `backend/tests/test_product_views_api.py`

**Interfaces:**
- Produces:
  - 테이블 `product_views`: `id` PK, `product_id` String(40) NOT NULL, `user_id` Integer FK users.id `ondelete="SET NULL"` nullable, `day_stem` String(2) nullable, `age_band` String(8) nullable, `gender` String(10) nullable, `created_at` timestamptz default now. 인덱스 `(product_id, created_at)`.
  - `crud.product_views.record_view(db, *, product_id: str, user_id: int | None, day_stem: str | None, age_band: str | None, gender: str | None) -> None` — 단발 쓰기라 내부에서 commit (backend/CLAUDE.md 규칙).
  - `schemas.product_views.ProductViewRequest`: `product_id: str = Field(pattern=r"^[a-z_]{1,40}$")`, `day_stem: str | None = Field(None, max_length=2)`, `age_band: str | None = Field(None, pattern=r"^\d{1,3}-\d{1,3}$")`, `gender: str | None = Field(None, max_length=10)`.
  - `POST /api/products/views` → 204, `get_optional_user` 사용, 게스트면 user_id=None. Router는 CRUD 직결 단일 호출.

- [ ] **Step 1: Write the failing tests** (`test_jobs_api.py`의 `_client` 패턴 + `override_db`, `db_user` 픽스처):
  - `test_record_view_guest`: 쿠키 없이 `{"product_id": "reunion"}` → 204, DB에 user_id NULL 행 1개.
  - `test_record_view_logged_in`: 토큰 + `{"product_id":"daily_fortune","day_stem":"임","age_band":"25-29","gender":"male"}` → 204, 행의 user_id == db_user.id, day_stem == "임".
  - `test_record_view_rejects_bad_id`: `{"product_id": "DROP TABLE"}` → 422.
  - 각 테스트는 만든 행을 삭제해 정리.
- [ ] **Step 2: Run** `cd backend && uv run pytest tests/test_product_views_api.py -v` → FAIL
- [ ] **Step 3: Implement** 모델·마이그레이션·crud·schema·router
- [ ] **Step 4: Run** `cd backend && uv run alembic upgrade head && uv run pytest tests/test_product_views_api.py -v` → PASS
- [ ] **Step 5: Commit** `feat: 상품 열람 기록 API`

### Task 5: 열람 기록 클라이언트

**Files:**
- Create: `packages/api-client/src/products.ts`; Modify: `packages/api-client/src/index.ts`
- Test: `packages/api-client/src/products.test.ts`
- Create: `apps/web/lib/products/track.ts`; Test: `apps/web/lib/products/track.test.ts`

**Interfaces:**
- Consumes: Task 3 `ProductId`, `ageBand`; Task 4 엔드포인트
- Produces:
  - `export interface ProductViewBody { product_id: string; day_stem?: string | null; age_band?: string | null; gender?: string | null }`
  - `export function recordProductView(api: ApiClient, body: ProductViewBody): Promise<void>` — `POST /api/products/views`
  - `apps/web/lib/products/track.ts`: `export function buildViewBody(productId: ProductId, profile: ProfileResponse | null, today: Date): ProductViewBody` 와 `export function trackProductView(productId: ProductId, profile: ProfileResponse | null): void` (내부에서 `recordProductView(api, ...)`를 호출하고 rejection은 `catch(() => {})`로 삼킨다 — 반환 Promise 없음)

- [ ] **Step 1: Write the failing tests**
  - api-client: 기존 `share.test.ts`처럼 가짜 ApiClient로 `recordProductView`가 `post('/api/products/views', body)` 호출.
  - web: `buildViewBody('reunion', null, today)` → `{ product_id: 'reunion' }`만; 대표 프로필(`birth_date '2001-08-17'`, `day_stem '임'`, `gender 'male'`) → `day_stem '임'`, `age_band '25-29'`, `gender 'male'`.
- [ ] **Step 2: Run** `pnpm --filter @sajuguri/api-client test && pnpm --filter web test` → FAIL
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run** 같은 명령 → PASS
- [ ] **Step 5: Commit** `feat: 상품 열람 기록 클라이언트`

### Task 6: 상품 문구·홈 문구 i18n

**Files:**
- Modify: `apps/web/messages/ko.json`, `apps/web/messages/en.json`

**Interfaces:**
- Produces 네임스페이스(ko·en 동시):
  - `products.<ProductId>.title`, `.desc`, `.counselPrompt`(coming_soon 4종만 — 상담 첫 메시지 힌트, 반말 한 문장)
  - `categories.all` + `categories.<ProductCategory>`
  - `home.hero.{freeDaily, unseen, cta, seenTitle, again, toCounsel, bubble}`, `home.counsel.{title, desc, cta}`, `home.situation.{title, some.title, some.desc, breakup.*, quit.*, money.*}`, `home.shelf.{ilgan, popular, more}`(ilgan은 `{stem}` 플레이스홀더 — "{stem} 일간에게 추천"), `home.ranking.title`("구리구리 추천"), `home.soon.{badge, title, body, cta, close}`, `home.search.{placeholder, empty, toCounsel}`
  - `nav.{menu, back, search, findIlgan, ilganChip}`(ilganChip은 `{hanja} {name} · {stem} 일간`), `drawer.{login, profile, manse, archive, language, theme, themeLight, themeDark, themeSystem, logout, close}`
- 문구는 시안·스펙 기준: 상황 2×2 = 썸 타는 중이에요/그 사람 마음이 궁금해, 헤어졌어요/다시 만날 수 있을까, 회사 그만둘까/지금 나가도 될까, 돈이 안 모여요/올해 재물 흐름은. 곧 나와요 시트 = "준비 중이에요. 지금은 이 고민 구리구리한테 먼저 얘기해 볼래?". 명리 용어 영문은 `backend/llm/prompts/glossary.py` 기준, 없으면 질문.

- [ ] **Step 1: Add keys** ko·en 동시
- [ ] **Step 2: Run** `node apps/web/scripts/check-i18n.mjs` → 누락 0 (아직 사용처 없음 — 키 집합 일치만 확인)
- [ ] **Step 3: Commit** `feat: 진열대 홈·드로어 문구 추가`

### Task 7: 앱 헤더 + ≡ 드로어, 하단 탭 제거

**Files:**
- Create: `apps/web/components/nav/AppHeader.tsx` (client), `apps/web/components/nav/Drawer.tsx` (client), `apps/web/components/nav/IlganChip.tsx`
- Modify: `apps/web/app/[locale]/layout.tsx` — `<TabBar />` 렌더 제거, `<AppHeader />` 추가, 래퍼 `pb-24 md:pt-24` → 헤더 높이에 맞게 조정
- Delete: `apps/web/components/TabBar.tsx` (사용처 없음 확인 후), `messages`의 `tab` 네임스페이스는 다른 사용처 없으면 제거
- Modify: `apps/web/app/[locale]/my/page.tsx` 등 — 드로어로 옮긴 항목이 빠지지 않았는지만 확인(이번 태스크에서 /my 레이아웃은 바꾸지 않음)

**Interfaces:**
- Consumes: Task 2 `Card`·`Button`·토큰, Task 6 `nav.*`·`drawer.*`, 기존 `LanguageToggleInline`, `LogoutButton`, `useSheetTransition`
- Produces:
  - `AppHeader({ user, repProfile }: { user: MeResponse | null; repProfile: ProfileResponse | null })` — 서버 레이아웃에서 `currentUser()`·`listProfiles()`로 받아 넘긴다. `usePathname()`이 `/`면 홈형(로고 · IlganChip · 검색 버튼 · ≡), 아니면 하위형(← 뒤로(`router.back()`, 히스토리 없으면 `/`) · 로고(홈 링크) · ≡). 검색 버튼은 Task 10의 `SearchSheet`를 연다(이 태스크에선 `onSearch` 자리만, Task 10에서 연결).
  - `IlganChip({ profile }: { profile: ProfileResponse | null })` — profile·day_stem 있으면 `nav.ilganChip` 칩 → `/manse/result?…`(기존 `lib/manse/query.ts`의 쿼리 생성 함수 재사용) ; 없으면 `nav.findIlgan` 버튼 → `/manse/new`. 이름은 `max-w` + `truncate`.
  - `Drawer({ open, onClose, user, profiles })` — 오른쪽 슬라이드, 딤 배경 클릭·Esc로 닫힘, 포커스 트랩. 항목 순서: 프로필/로그인(→ `/my` 또는 로그인) · 내 만세력(→ `/manse`) · 보관함(→ `/my/history`) · 언어(`LanguageToggleInline`) · 로그아웃(로그인 시). **화면 모드 항목은 렌더하지 않는다**(Task 20).
  - 운세 스토리 오버레이(z-50)가 헤더를 덮는지 확인 — 헤더 z-index는 design.md §9.2 단계 중 오버레이보다 낮게.

- [ ] **Step 1: Implement** 세 컴포넌트와 레이아웃 변경
- [ ] **Step 2: Run** `pnpm --filter web typecheck && node apps/web/scripts/check-i18n.mjs` → PASS
- [ ] **Step 3: 확인** `pnpm dev` 후 360px 폭에서: `/`, `/manse`, `/my`, `/report/new`, `/fortune` 진입 → 하단 탭 없음, 모든 화면에서 ≡로 만세력·보관함·마이 도달, 10자 한글 이름 프로필로 칩 말줄임·가로 스크롤 없음, 운세 스토리가 헤더를 덮음, 키보드로 드로어 열고 Esc로 닫힘.
- [ ] **Step 4: Commit** `feat: 하단 탭을 앱 헤더와 메뉴 드로어로 교체`

### Task 8: 홈 히어로 — 오늘의 운세 카드 + 캐러셀

**Files:**
- Create: `apps/web/lib/home/fortuneSummary.ts`; Test: `apps/web/lib/home/fortuneSummary.test.ts`
- Create: `apps/web/components/home/HeroCarousel.tsx` (client), `apps/web/components/home/FortuneHeroCard.tsx` (client), `apps/web/components/home/CounselCard.tsx`

**Interfaces:**
- Consumes: `loadCachedStory`, `buildBirthKey` (`lib/fortune/cache.ts`), 기존 `FortuneBannerClient`의 진입 동작(만세력 선택 시트 / 게스트 생년월일 입력 → 운세), Task 2·6
- Produces:
  - `export type FortuneSummary = { seen: false } | { seen: true; score: number; headline: string }`
  - `export function summarizeStory(story: DailyStoryResponse | null): FortuneSummary` — overall 카드(`kind==='overall'`)의 `score`·`headline`; 없거나 score 없음 → `{ seen: false }`
  - `FortuneHeroCard({ profiles, isLoggedIn })` — 마운트 후 대표 프로필 birthKey + 오늘(로컬 날짜)로 캐시 조회 → summarize. 안 본 날: "매일 무료" 리본·`home.hero.unseen`·너구리 + 말풍선·[`home.hero.cta`]. 본 날: 점수 + 헤드라인 + [`home.hero.again`] + `home.hero.toCounsel` 링크(`/chat`). 탭 동작은 `FortuneBannerClient`를 감싸 재사용. 첫 렌더는 안 본 상태(SSR 일치), 캐시 확인 후 교체.
  - `HeroCarousel({ slides }: { slides: ReactNode[] })` — CSS scroll-snap 가로 슬라이드 + 페이지 점, 자동 넘김 없음. 슬라이드: `[FortuneHeroCard, CounselCard 큰 버전]`.
  - `CounselCard({ size }: { size: 'hero' | 'row' })` — `Card tone="counsel"`, `/chat` 링크, 클릭 시 `trackProductView('guriguri_counsel', …)`.

- [ ] **Step 1: Write the failing test** `summarizeStory(null)` → `{seen:false}`; overall `{score:72, headline:'말 한마디가 판을 바꾸는 날'}` 포함 스토리 → `{seen:true, score:72, headline:'말 한마디가 판을 바꾸는 날'}`; cards에 overall 없음 → `{seen:false}`; overall에 score 없음 → `{seen:false}`.
- [ ] **Step 2: Run** `pnpm --filter web test` → FAIL
- [ ] **Step 3: Implement** 함수와 세 컴포넌트
- [ ] **Step 4: Run** `pnpm --filter web test && pnpm --filter web typecheck` → PASS
- [ ] **Step 5: Commit** `feat: 홈 히어로 오늘의 운세 카드와 캐러셀`

### Task 9: 홈 본문 — 카테고리 탭·내 상황·선반·랭킹·곧 나와요

**Files:**
- Modify: `apps/web/app/[locale]/page.tsx` (전면 교체; `searchParams.cat` 읽기)
- Create: `apps/web/components/home/CategoryTabs.tsx`, `SituationGrid.tsx`, `ProductShelf.tsx`, `PosterCard.tsx`, `RankList.tsx`, `ProductGrid.tsx`, `ComingSoonSheet.tsx`(client), `ProductLink.tsx`(client)
- Modify: `apps/web/app/[locale]/chat/page.tsx` 또는 상담 시작 진입점 — `?topic=<ProductId>`가 있으면 새 세션 첫 입력창에 `products.<id>.counselPrompt`를 채워 둔다(자동 전송 안 함)

**Interfaces:**
- Consumes: Task 3 전부, Task 5 `trackProductView`, Task 6 문구, Task 8 히어로
- Produces:
  - `page.tsx`: `cat`이 `CATEGORY_ORDER`에 있으면 `<CategoryTabs active={cat}/>` + `<ProductGrid products={productsInCategory(cat)}/>`만; 아니면(전체) 순서대로 `CategoryTabs active="all"` → `HeroCarousel` → `CounselCard size="row"` → `SituationGrid` → `ProductShelf shelf={curatedShelf(repProfile?.day_stem ?? null)}` → `RankList ids={curatedRanking()}`.
  - `CategoryTabs({ active }: { active: ProductCategory | 'all' })` — `Link` `?cat=` (전체는 쿼리 없음), 가로 스크롤 가능한 탭 줄(탭 줄 자체만 overflow-x), 활성 = 텍스트 강조 + accent 밑줄.
  - `ProductLink({ product, profile, children })` — available: `trackProductView` 후 `href`로 이동; coming_soon: `ComingSoonSheet` 열기.
  - `ComingSoonSheet({ product, open, onClose })` — `home.soon.*` 문구, [상담하기] → `/chat?topic=<id>` (+ `trackProductView('guriguri_counsel')`).
  - `PosterCard({ product })` — 3:4 비율 카드, 상품 일러스트(배경 투명 PNG) + `--font-display` 제목 + 한 줄 설명, coming_soon이면 `home.soon.badge` 배지. 배경은 상품별 surfaceSoft 계열 토큰(카테고리→토큰 매핑 상수).
  - `ProductShelf({ shelf, stem })` — 제목 = `kind==='ilgan'` ? `home.shelf.ilgan`({stem}) : `home.shelf.popular`; 가로 스크롤 선반(선반 컨테이너만 overflow-x).
  - `RankList({ ids })` — 제목 `home.ranking.title`, 번호·썸네일·제목·설명 행.
  - 기존 `FortuneBannerClient` 배너·`BrutalCard` 기반 카드 목록·`LanguageToggleCompact`(드로어로 이동)는 홈에서 제거.

- [ ] **Step 1: Implement** 컴포넌트와 page.tsx
- [ ] **Step 2: Run** `pnpm --filter web typecheck && pnpm --filter web test && node apps/web/scripts/check-i18n.mjs` → PASS
- [ ] **Step 3: 확인** `pnpm dev` 360px·640px: 비로그인 홈(선반 popular, 칩 "내 일간 찾기"), 로그인+대표 만세력(선반 "임 일간에게 추천"), `?cat=love`(그리드에 썸·재회·궁합·상담), 곧 나와요 카드 → 시트 → 상담 입력창에 힌트 채워짐, `/en` 영어 문구로 포스터 제목 넘침 없음, 페이지 가로 스크롤 없음, 네트워크 탭에서 열람 POST 204(백엔드 꺼도 화면 정상).
- [ ] **Step 4: Commit** `feat: 진열대 홈 본문과 곧 나와요 시트`

### Task 10: 검색 시트

**Files:**
- Create: `apps/web/components/home/SearchSheet.tsx` (client)
- Modify: `apps/web/components/nav/AppHeader.tsx` (검색 버튼 연결)

**Interfaces:**
- Consumes: Task 3 `searchProducts`, Task 9 `PosterCard`/`ProductLink`, Task 6 `home.search.*`
- Produces: `SearchSheet({ open, onClose, profile })` — 입력(자동 포커스) 즉시 `searchProducts(q, locale)` 결과 목록; 결과 0개이고 q가 비어있지 않으면 `home.search.empty` + [`home.search.toCounsel`] → `/chat` (입력어를 `?q=`로 넘겨 Task 9의 상담 입력 채우기와 같은 방식으로 입력창에 채움).

- [ ] **Step 1: Implement**
- [ ] **Step 2: Run** `pnpm --filter web typecheck && node apps/web/scripts/check-i18n.mjs` → PASS
- [ ] **Step 3: 확인** "재회"·" 이 직 "·영어 로케일 "reunion"·"없는말" 각각 기대 결과, Esc로 닫힘
- [ ] **Step 4: Commit** `feat: 상품·고민 검색 시트`

### Task 11: 일러스트 생성 스크립트 + 글꼴 선택 + 문서

**Files:**
- Create: `backend/scripts/generate_product_art.py`, `backend/scripts/product_art_prompts.json`
- Create (생성물): `apps/web/public/products/<ProductId>.png`
- Modify: `packages/core/src/catalog/products.ts` (`art`를 `/products/<id>.png`로 — 검수 통과분만)
- Modify: `apps/web/app/[locale]/layout.tsx`, `apps/web/app/globals.css` (`--font-display` 실제 글꼴)
- Modify: `docs/design.md` (전면 재작성), `AGENTS.md` (G2 그라데이션·브루탈 문구)

**Interfaces:**
- 스크립트: `uv run python scripts/generate_product_art.py --only reunion,money_flow --dry-run` — 프롬프트 JSON(`{ "<ProductId>": "<장면 설명(영문)>" }` + 공통 스타일 문구: 굵은 외곽선 스티커, 노란 너구리 캐릭터, 검은 갓, 배경 투명)을 읽어 `openai` `images.edit(model="gpt-image-1", image=[참조 스티커들], prompt=…, background="transparent", size="1024x1024", quality="medium")` 호출, 결과를 `apps/web/public/products/<id>.png`로 저장. `--dry-run`은 호출 없이 대상·예상 비용만 출력. 키는 `OPENAI_API_KEY` 환경변수. 이미 파일이 있으면 `--force` 없이는 건너뜀.
- 참조 이미지: `apps/web/public/mascot/fortune.png`, `love.png`, `thumbsup.png`.
- 대상 약 12장: 9개 상품 + 빈 상태(`empty`) + 로그인 안내(`login`) + 검색 결과 없음(`search_empty`).

- [ ] **Step 1: Implement 스크립트 + 프롬프트 JSON**, `--dry-run` 실행 → 대상 12개·예상 비용 출력 확인
- [ ] **Step 2: 사용자에게 예상 비용 알리고 승인 후 실행** (총 $10 이내, 재생성 포함 — 누적 비용을 기록)
- [ ] **Step 3: 생성 결과를 사용자에게 보여 검수** (Artifact 또는 SendUserFile), 반려분만 `--only … --force`로 재생성
- [ ] **Step 4: 검수 통과분 `art` 경로 교체**, `pnpm --filter @sajuguri/core test` → PASS
- [ ] **Step 5: 디스플레이 글꼴 후보 3개(Google Fonts OFL 한글: Jua, Do Hyeon, Black Han Sans) 비교 시안을 사용자에게 보여 선택받고** `next/font/google`로 `--font-display` 연결
- [ ] **Step 6: `docs/design.md` 재작성** — 스펙 §3(방향·모드·글꼴·아이콘)·§4 네비·§5 홈 구성·토큰 표(Task 1 값)·Card/Button 규칙. 브루탈 2단계·하단 탭·Y2K 크롬 섹션 삭제, "다크모드 v1 미지원" 삭제(Task 20 전까지 라이트 고정이라고 명시). `AGENTS.md` G2: "칩·버튼·말풍선·브루탈 강도 2단계" → 새 규칙, 그라데이션 예외에 "다크 포스터 카드의 은은한 방사형 배경" 추가.
- [ ] **Step 7: Commit (분리)** `feat: 상품 일러스트 생성 스크립트` / `feat: 상품 일러스트 적용` / `feat: 디스플레이 글꼴 적용` / `docs: 새 디자인 시스템 문서화`

**1차 배포:** Task 1~11 전부 통과 후 `pnpm build && pnpm test && pnpm typecheck`, `cd backend && uv run pytest` → PASS 확인, dev → main 머지(배포 시 alembic 0018 자동 적용).

---

## 화면별 교체 (Task 12~21, 태스크 단위 배포)

각 화면 태스크의 공통 절차:
1. 대상 파일에서 `BrutalCard`·`shadow-brutal*`·`shadow-pop*`·`shadow-gloss`·`border-ink`·`bg-bg-base`·`--chrome*` 사용을 `Card`/`Button`/`c-*` 토큰으로 교체한다. 기능·데이터 흐름은 그대로.
2. 검증: `grep -rnE "BrutalCard|shadow-brutal|shadow-pop|shadow-gloss|border-ink|chrome-" <대상 경로>` → 0건, `pnpm --filter web typecheck && pnpm --filter web test && node apps/web/scripts/check-i18n.mjs` → PASS.
3. 360px에서 화면 확인 + 해당 화면 기능 목록 전부 동작.
4. 커밋 `refactor: <화면> 새 디자인 적용`.

### Task 12: 만세력 입력·목록
대상: `app/[locale]/manse/page.tsx`, `manse/new/*`, `components/manse/{BirthInputForm,InputForm,SavedList,SavedListClient,RecentList,RecentEnricher,MansePickerSheet,ManseEntryButton,SaveButton,SaveToMyButton}.tsx`.

### Task 13: 만세력 분석 (구성 보존)
대상: `manse/result/*`, `components/manse/{ResultView,IljuHero,PillarCard,GanjiColumn,DaeUnTimeline,YeonWolUn,IlJinCalendar,HapChungPanel,StrengthCard,TenGodsCard,WuxingBalanceCard,WuxingFeatureTable,DetailAccordion,TagChips,ShareButton}.tsx`, `components/ui/{Chip,Accordion}.tsx`.
- **일주 히어로·기둥 카드 배치는 그대로** (사용자 확정), 색·테두리만.
- 오행색은 `ohaengByTheme.light`/`ohaengTintByTheme.light` 값(CSS 변수로 추가)으로.
- G3 대조: 대운/월운/연운 슬라이더, 일진 캘린더, 합충 패널, 신살 테이블, 강약 바, 오행 특성 참고표가 개편 전후 모두 보이는지 체크리스트로 확인하고 커밋 메시지 본문에 결과 기록.

### Task 14: 10탭 리포트
대상: `report/*`, `components/report/*`, `components/ui/{Markdown,PageHeading}.tsx`.

### Task 15: 궁합
대상: `compatibility/new|[id]|shared/*`, `components/compatibility/*` (점수·오행 흐름도 유지).

### Task 16: 한 번 물어보기
대상: `question/*`.

### Task 17: 기존 상담 (토큰만)
대상: `chat/*`, `components/chat/*`. 밤의 상담실은 2번 스펙 — 여기선 토큰 교체만.

### Task 18: 마이·보관함
대상: `my/*`, `components/my/*`, `lib/records/cards.tsx`. 드로어 항목과 겹치는 진입은 정리하되 기능(리포트 목록·운세 기록·공유 관리·설정·삭제) 보존.

### Task 19: 공유 페이지·OG 이미지·기타
대상: `share/*`, `compatibility/shared/*`, `**/opengraph-image.tsx`, `auth/done`, `not-found`, `components/ui/ShareModal.tsx`, `LanguageToggleCompact.tsx`(사용처 없으면 삭제). 운세 스토리 3파일은 제외.
- 이 태스크 후 `grep -rnE "BrutalCard|shadow-brutal|shadow-pop|shadow-gloss" apps/web --include=*.tsx`가 운세 스토리 3파일 외 0건이어야 한다.

### Task 20: 다크 모드 켜기

**Files:**
- Create: `apps/web/lib/theme.ts`; Test: `apps/web/lib/theme.test.ts`
- Create: `apps/web/components/nav/ThemeToggle.tsx` (client)
- Modify: `apps/web/app/[locale]/layout.tsx` (서버에서 쿠키 `theme` 읽어 `<html data-theme>`·`themeColor`, `system`이면 속성 없이 두고 CSS `@media (prefers-color-scheme: dark)`가 `:root:not([data-theme="light"])`에 다크 값 적용), `globals.css` (다크 미디어쿼리 블록 추가, `body` 배경을 `--c-bg`로 전환)
- Modify: `apps/web/components/nav/Drawer.tsx` (화면 모드 항목 추가)

**Interfaces:**
- Produces: `export type ThemePref = 'light' | 'dark' | 'system'`; `export function parseThemePref(raw: string | undefined): ThemePref` (알 수 없는 값 → `'system'`); `export const THEME_COOKIE = 'theme'`; `ThemeToggle` — 세 값 라디오, 선택 시 쿠키(1년) 쓰고 `document.documentElement.dataset.theme` 즉시 갱신(system이면 속성 제거).

- [ ] **Step 1: Write the failing test** `parseThemePref('dark')==='dark'`, `parseThemePref(undefined)==='system'`, `parseThemePref('blue')==='system'`
- [ ] **Step 2: Run** `pnpm --filter web test` → FAIL
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run** `pnpm --filter web test && pnpm --filter web typecheck` → PASS
- [ ] **Step 5: 확인** 다크 OS + system, 라이트 고정, 다크 고정 각각에서 홈·만세력 분석·리포트·궁합·마이·공유 페이지 글자 대비, 새로고침 시 깜빡임 없음, 운세 스토리는 모드와 무관하게 동일
- [ ] **Step 6: Commit** `feat: 다크 모드와 화면 모드 선택`

### Task 21: 브루탈 유틸리티 제거
- Delete: `apps/web/components/ui/BrutalCard.tsx`; `globals.css`에서 `--shadow-brutal*`, `--shadow-pop*`, `--shadow-gloss`, `--chrome*`, `--holo`, `--specular`, 브루탈 눌림 피드백 규칙, 옛 `--bg-base`·`--ink` 등 **웹 전용** 옛 변수(운세 스토리 3파일이 쓰는 것은 남김 — grep으로 확인).
- `packages/design`의 옛 export는 **남긴다**(모바일).
- 검증: `pnpm build && pnpm test && pnpm typecheck` → PASS, `grep -rn "BrutalCard" apps/web` → 0건.
- Commit `refactor: 브루탈 유틸리티 제거`
