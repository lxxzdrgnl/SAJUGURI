# 사주구리 디자인 시스템 — "진열대 카탈로그"

> 2026-10-21 개편으로 확정. 이전 "비비드 캔디 브루탈"(굵은 잉크 테두리 + 오프셋 그림자,
> 하단 탭 바, Y2K 크롬)은 폐기했다.
> 설계 배경·결정 근거: `docs/superpowers/specs/2026-10-21-catalog-home-redesign-design.md`
> 구현 계획: `docs/superpowers/plans/2026-10-21-catalog-home-redesign.md`

---

## 1. 방향

- **넓은 여백 + 얇은 라인 + 둥글고 큰 카드.** 화면 장식은 줄이고, 개성은
  **너구리 스티커 일러스트**와 **굵은 손글씨풍 제목 글꼴(주아)**이 맡는다.
- 홈은 상품 진열대(카탈로그)다. 주력 상품은 **오늘의 운세**, 그다음이 **구리구리 상담**.
- 브루탈 요소(2px 잉크 테두리, 오프셋 그림자, 눌림 섀도)는 쓰지 않는다.
- 포인트 컬러는 **옐로 `#FFD900`** 하나. 로고 "구리" 하이라이트, 주요 버튼, 활성 탭 표시에만 쓴다.
- **마스코트**: 너구리 ("사주**구리**" = 너**구리**). 스티커 이미지는 `apps/web/public/mascot/*.png`
  (배경 투명). 상품별 새 일러스트는 추후 추가 — 그전까지 기존 스티커를 돌려쓴다.
- **로고타입**: `사주` + 옐로 하이라이트 박스 `구리`. 문자열은 i18n `nav.logo`.

---

## 2. 컬러 토큰

색은 **의미 토큰만** 쓴다. 컴포넌트에 임의 HEX 금지.
원천은 `packages/design/src/tokens.ts`(`semantic`, `ohaengByTheme`, `ohaengTintByTheme`,
`posterByTheme`), 웹은 `apps/web/app/globals.css`의 `--c-*` CSS 변수가 미러한다
(라이트 = `:root`, 다크 = `:root[data-theme="dark"]` + 시스템 다크 미디어쿼리 블록 — §3). Tailwind 유틸은 `@theme inline`의
`--color-c-*` 매핑으로 생긴다 (`bg-c-bg`, `text-c-text-sub` …).

새 색이 필요하면 `--c-*` 토큰을 `:root` + 다크 두 블록 + `@theme` 매핑 네 곳에
함께 추가한다. 공유 값이면 `packages/design`에도 올린다.

### 2.1 의미 토큰

| 토큰 (`--c-*`) | Tailwind | 라이트 | 다크 | 용도 |
|---|---|---|---|---|
| `bg` | `bg-c-bg` | `#FFFFFF` | `#121212` | 화면 배경 |
| `surface` | `bg-c-surface` | `#FFFFFF` | `#1A1A1A` | 카드·시트 표면 |
| `surface-soft` | `bg-c-surface-soft` | `#FAF6EC` | `#232323` | 크림 카드, 입력 배경, 비활성 칩 |
| `line` | `border-c-line` | `#E7E2D6` | `#333333` | 1px 구분선·카드 테두리 |
| `text` | `text-c-text` | `#14161C` | `#F5F5F5` | 본문·제목 |
| `text-sub` | `text-c-text-sub` | `#5B606B` | `#A8ADB7` | 보조 텍스트 |
| `accent` | `bg-c-accent` | `#FFD900` | `#FFD900` | 주요 행동·활성 표시 |
| `on-accent` | `text-c-on-accent` | `#14161C` | `#14161C` | 옐로 위 글자 |
| `danger` | `text-c-danger` | `#D92D20` | `#FF6B5E` | 삭제·오류 |
| `counsel-bg` / `counsel-fg` | `bg-c-counsel-bg` / `text-c-counsel-fg` | `#04332F` / `#E9F4F1` | 동일 | 구리구리 상담 카드 (밤의 상담실 톤) |
| `scrim` | `bg-c-scrim` | 반투명 검정 | 반투명 검정 | 드로어·시트 뒤 딤 |

### 2.2 포스터 팔레트 (홈 진열대)

상품 카테고리별 포스터 카드 배경. `--c-poster-*`, Tailwind `bg-c-poster-*`.
카테고리 → 톤 매핑은 `apps/web/lib/products/posterTone.ts`.

| 톤 | 라이트 | 다크 |
|---|---|---|
| butter | `#FFF3C4` | `#3A3217` |
| rose | `#FDE4EA` | `#3A2129` |
| lilac | `#ECE7FA` | `#2A2540` |
| peach | `#FFE8D9` | `#3B281D` |
| sky | `#E2EEFB` | `#182A3B` |
| mint | `#DDF3EA` | `#17332A` |

포스터 위 글자는 `text-c-text`. 대비는 `packages/design` 테스트가 검사한다.

### 2.3 오행 5색

`--c-oh-{mok,hwa,to,geum,su}`(글자·채움)과 `--c-oh-*-tint`(기둥 카드 배경).
코드에서는 `apps/web/lib/ohaeng.ts`의 `ohaengVar()` / `ohaengTintVar()`로 얻는다.
(옅은 배경이 필요하면 `color-mix(in srgb, var(--c-oh-x) 10%, transparent)`. HEX 헬퍼는 없다 — 항상 CSS 변수를 쓴다.)

| 오행 | 라이트 | 라이트 틴트 | 다크 | 다크 틴트 |
|---|---|---|---|---|
| 목 | `#008A57` | `#E9FAF1` | `#2FD28F` | `#12261D` |
| 화 | `#E05A00` | `#FFEEDD` | `#FF8A3D` | `#2B1B10` |
| 토 | `#A67C00` | `#FFF6D1` | `#E5B820` | `#2A2410` |
| 금 | `#6B7280` | `#EEF0F3` | `#B6BCC8` | `#222428` |
| 수 | `#2B7FD1` | `#DCEFFB` | `#5BB0F2` | `#12212E` |

길흉 칩·차트용 별칭: `--c-lucky-bg/fg`, `--c-unlucky-bg/fg`, `--c-chart-accent`, `--c-chart-saeng`.

### 2.4 일간 고정색 (모드 무관)

**일주 히어로 / 마스코트 / 아바타 배경 = 일간 천간 색** (사용자 확정, 두 모드 동일):
갑·을 푸른 `#7FC7BE` / 병·정 붉은 `#EA6845` / 무·기 황금 `#FFD900` / 경·신 은빛 `#E8EAED` /
임·계 웜그레이 `#8B8178`. 히어로에 **띠 닉네임**(천간 색 + 지지 동물 — "회색 쥐"/"Gray Rat")을
표기한다. 단일 출처 `lib/manse/ganjiNickname.ts`. 히어로 위 글자는 `text-c-on-accent`.

### 2.5 그라데이션

앱 본체의 카드·배너는 **단색**. 예외는 운세 스토리 하나뿐이다.
- **오늘의 운세 스토리** — 모드와 무관하게 기존 비비드 룩(딥 틸 `#00857D → #04332F`,
  점수 `#FF8A2E`, 프로그레스 `#FFD900`). `FortuneStoryPage`·`StoryCard`·`SummaryCard`는 동결.
- (허용만 된 예외) 다크 포스터 카드의 은은한 방사형 배경 — 아직 쓰는 곳 없음.

---

## 3. 모드

- 라이트 / 다크 / 시스템, **기본 = 시스템**. 선택은 드로어에서 하고 쿠키에 저장해 SSR 깜빡임을 막는다.
- 같은 구성, 색만 다르다. 라이트 = 흰 바탕 + 크림·파스텔 카드, 다크 = 검정에 가까운 바탕 + 깊은 포스터 카드.
- 구현: 쿠키 `theme`(`light`/`dark`/`system`, `lib/theme.ts`)을 `[locale]/layout.tsx`가 읽어
  라이트·다크면 `<html data-theme>`을 SSR로 박고, 시스템이면 속성 없이 둔다. 다크 값은
  `:root[data-theme="dark"]`와 `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }`
  두 블록에 **같은 목록**으로 있다(`lib/theme.test.ts`가 일치 검사). 다크 토큰을 고치면 둘 다 고친다.
  `theme-color`·`color-scheme`도 모드를 따른다(라이트 `#FFFFFF` / 다크 `#121212`).
- 구리구리 상담실(다음 프로젝트)은 두 모드 모두 "밤의 상담실"(딥 틸 밤하늘). 밤하늘 톤은 상담실에서만 쓴다.

---

## 4. 글꼴

| 역할 | 글꼴 | 사용 |
|---|---|---|
| 제목·상품명·히어로·로고 | **주아 (Jua)** — `next/font/google`, `--font-display`, 유틸 `font-display` | 400 한 굵기뿐이라 **반드시 `font-normal`과 함께** 쓴다 (가짜 볼드 금지) |
| 본문·UI | 시스템 고딕 스택 (`--font-sans`, Tailwind 기본) | Pretendard는 아직 로드하지 않는다 |
| 간지 한자·한글 | 본문과 같은 고딕 (`font-serif` 유틸이 고딕 스택을 가리킨다) | 명조로 튀지 않게 통일 |

---

## 5. 형태·간격

| 대상 | 클래스 | 값 |
|---|---|---|
| 카드·포스터·히어로 | `rounded-card` | 20px |
| 바텀시트 위쪽 | `rounded-t-card` | 20px |
| 버튼·칩·검색창·토글 | `rounded-pill` | 알약 |

- 테두리는 **1px `border-c-line`** 하나. 강조(일주 기둥·현재 대운·오늘 일진)는 1.5px `c-text` 라인.
- 그림자 없음. 눌림은 `Button`이 `active:scale-[0.98]`, 그 밖의 버튼은 전역 규칙이 `translateY(1px)`.
- 레거시 `rounded-sm/md/lg/xl/2xl/3xl`은 축소 스케일(4~16px)로 덮어써 둔 채 남아 있다(기존 사용처 약 40곳). 새 코드는 위 표의 클래스만 쓴다.

---

## 6. 컴포넌트

### 6.1 Card — `components/ui/Card.tsx`
`tone`: `plain`(c-surface + 1px 라인) · `soft`(c-surface-soft, 무테) · `counsel`(상담 딥 틸).
항상 `rounded-card`, 그림자 없음.

### 6.2 Button — `components/ui/Button.tsx`
`variant`: `primary`(옐로) · `secondary`(표면 + 1px 라인) · `ghost`(투명) · `danger`(파괴적 행동, `c-danger`). 기본 `type="button"`, disabled는 반투명 + 눌림 없음.
`size`: `sm`(h-8) · `md`(h-11). 알약, `font-extrabold`.
Link에 같은 모양이 필요하면 `buttonClass(variant, size)`를 쓴다.
**옐로 primary는 화면의 주요 행동에만** 쓴다 — 배지·장식 칩에 옐로를 쓰지 않는다.

### 6.3 칩
알약, 1px 라인 또는 `c-surface-soft` 배경. 의미는 배경 틴트로만 (길신 = `c-lucky-*`, 흉살 = `c-unlucky-*`).
활성 탭 칩 = `bg-c-accent text-c-on-accent`.

### 6.4 시트·드로어
뒤 화면 `bg-c-scrim`, 본체 `bg-c-surface` 또는 `bg-c-bg`, 바텀시트는 위쪽만 둥글게(`rounded-t-card`로 통일),
바깥 탭·Esc로 닫힘. 참고 구현: `components/home/ComingSoonSheet.tsx`, `components/nav/Drawer.tsx`.

### 6.5 아이콘
**UI 이모지 금지.** 스트로크 SVG (24px viewBox, `stroke-width: 2`, round cap/join).

### 6.6 말풍선 (현재 상담)
밤의 상담실 전까지는 토큰만 바꾼 상태 — 유저 = `c-accent` 배경, AI = `c-surface` + 1px 라인.
말풍선 안 Markdown은 컨테이너가 글자색을 지정한다.

---

## 7. 네비게이션

- **하단 탭 바 없음.** 전역 `AppHeader`(sticky, `z-30`) + 오른쪽 **≡ 드로어**.
- **홈 헤더**: 로고 · 일간 칩 · 검색 · ≡.
  - 일간 칩 `壬 임수 · 임수 일간` (en: `{hanja} {name} · Day Master`) → 대표 만세력 분석 화면.
  - 만세력이 없으면 칩 자리에 **"내 일간 찾기"** → 생년월일 입력.
- **하위 화면 헤더**: ← 뒤로 + 제목 + ≡. 페이지 안에 따로 뒤로 버튼을 두지 않는다.
- **≡ 드로어** 순서: 프로필·로그인 → 내 만세력 목록 → 보관함(상담·리포트·궁합·운세 기록, 공유 관리)
  → 화면 모드·언어 → 로그아웃. **홈의 상품 입구는 드로어에 중복하지 않는다.** 공지·고객센터 없음.

---

## 8. 홈 구성 (위 → 아래)

1. 헤더 (§7)
2. **검색** — 상품 + 고민 키워드 (`searchProducts`). 결과 없으면 "구리구리한테 이 고민 상담하기".
3. **카테고리 탭** — 전체 = 큐레이션 홈, 나머지 = 그 카테고리 포스터 그리드 필터.
4. **히어로 캐러셀** — 첫 장은 항상 오늘의 운세 (안 본 날: "매일 무료" + 넘겨 보기 / 본 날: 점수 + 한 줄 요약
   + "구리구리랑 더 얘기"), 뒤에 추천 2~3장.
5. **구리구리 상담실 카드** (`Card tone="counsel"`) → `/chat`.
6. **요즘 어떤 고민이야?** 2×2 상황 그리드 → 해당 테마 상품.
7. **맞춤 선반** — 로그인: "{일간} 일간에게 추천", 게스트: "처음이라면 이것부터".
8. **랭킹** — "구리구리 추천".

> 선반·랭킹은 지금 **큐레이션**이다. 실제 통계로 바꾸기 전에는 "많이 본" 같은 문구를 쓰지 않는다.
> 상품 열람은 `POST /api/products/views`로 이미 수집 중이다 (fire-and-forget).

- 상품 정의는 데이터: `packages/core/src/catalog/*` (`PRODUCTS`, 상태 available/coming_soon, 키워드, ko/en).
- **곧 나와요** 상품 → 안내 시트 + [구리구리 상담하기] (주제를 첫 메시지 힌트로 넘김, `?topic=`).

---

## 9. 화면별 메모

### 9.1 만세력 분석 — "일주 히어로 + 기둥 카드" (배치 고정)
배치는 그대로 두고 색·테두리만 새 시스템을 따른다 (G3: 재배치이지 축소가 아니다).
섹션 순서는 레거시 `ResultPanel.vue` 기준: 팔자 → 합충 → 신살/12운성 상세 → 오행 특성표 →
오행 밸런스(보정 토글 2개 — 합 변화·조후 궁성 — 필수) → 십성 → 강약/용신(8단계 바 + 분포 그래프) →
대운 → 연운/월운 → 일진. 하단 CTA: 리포트(primary) · 상담·공유(secondary).

### 9.2 오늘의 운세 스토리
동결 (§2.5). 진입은 홈 히어로 → 만세력 선택 시트(저장 목록 + 직접 입력).

---

## 10. 말투(콘텐츠 톤)

| 표면 | 톤 | 규칙 |
|---|---|---|
| 리포트·채팅 | **모던 해설가** — 존댓말 | 길고 풍부하게(탭당 3~4문단). 억지 위트·이모지 금지 |
| 운세 스토리 | **직설 친구** — 반말, 짧은 명령형 | "64점. 지갑 열되 큰 건 멈춰." |
| 홈 카피 | 친근한 반말 | "요즘 어떤 고민이야?" |
| UI 표기 | — | "프로필" 대신 **"만세력"** |

---

## 11. 레이아웃·레이어·접근성

- 전 화면 **모바일 단일 컬럼 max-width 640px** 가운데 정렬. PC 전용 레이아웃 없음. 가로 스크롤 금지.
- 화면 배경은 `body`가 `var(--c-bg)`로 칠한다. 페이지가 따로 배경을 칠하지 않는다.

### z-index

| 층 | 값 | 용도 |
|---|---|---|
| 배경 아트 | `z-0` | 장식 |
| 콘텐츠·드롭다운 | `z-10` | 본문, 자동완성 |
| 헤더 | `z-30` | 전역 AppHeader |
| 시트·드로어 백드롭 | `z-40` | 딤 |
| 시트·모달·스토리 패널 | `z-50` | 바텀시트 본체, 드로어, 공유 모달, 운세 스토리 |

### 포커스 링
전역 `:focus-visible`이 바깥으로 3px 링을 띄운다(`globals.css`). 입력창에 `outline-none` 금지.
보더 없는 투명 입력은 감싼 컨테이너에 `.focus-ring-within`.
