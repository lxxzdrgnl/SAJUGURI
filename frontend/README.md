# Frontend — Vue.js 3 + Nuxt.js

## 개요

사주 입력부터 만세력 리포트, 오늘의 운세, 한줄 상담, 공유까지 모든 UI를 담당하는 Nuxt.js 3 앱입니다.

---

## 실행

```bash
cd frontend
pnpm install
cp .env.example .env   # NUXT_PUBLIC_API_BASE=http://localhost:8000
pnpm dev               # http://localhost:3000
```

```bash
pnpm build && pnpm preview   # 프로덕션 빌드
```

---

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | 백엔드 API 주소 |

---

## 페이지 구조

| 경로 | 설명 |
|---|---|
| `/` | 홈 — 대표 만세력 카드, 일진, 서비스 목록 |
| `/profile` | 만세력 — 사주 입력 + 12단계 리포트 |
| `/my-profiles` | 내 만세력 목록 — 선택 → 재계산 |
| `/daily` | 오늘의 운세 — 명리 기반 6카테고리 |
| `/daily/share/[token]` | 오늘의 운세 공유 페이지 |
| `/question` | 한줄 상담 — 고민 입력 → AI 단답 |
| `/question/history` | 상담 히스토리 |
| `/question/share/[token]` | 상담 결과 공유 페이지 |
| `/share/[token]` | 만세력 결과 공유 페이지 |
| `/login` | 로그인 |
| `/auth/callback` | Google OAuth2 콜백 |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | Nuxt.js 3 |
| UI | Vue.js 3 (Composition API) |
| 상태 관리 | Pinia |
| 스타일 | Tailwind CSS + 전역 CSS 변수 (`assets/css/main.css`) |
| 차트 | Chart.js |
| 패키지 매니저 | pnpm |

---

## 공통 컴포넌트

> 아래 컴포넌트가 이미 구현되어 있다. 새 기능 추가 시 중복 구현하지 말고 그대로 가져다 써라.

### `components/ui/`

| 컴포넌트 | Props | 설명 |
|---|---|---|
| `<LoadingSpinner>` | `size?: 'sm'\|'md'\|'lg'` | 로딩 스피너 |
| `<UiShareModal>` | `v-model:show`, `url` | 링크 공유 모달. 열릴 때 자동 클립보드 복사 |
| `<UiInfoTooltip>` | `text` | 용어 설명 말풍선 (호버/탭 토글) |

### `components/`

| 컴포넌트 | Props / Slot | 설명 |
|---|---|---|
| `<AppDialog>` | `v-model:show`, `title`, `desc?`, `cancelText?` + slot | 확인/안내 다이얼로그 |

### `components/saju/`

| 컴포넌트 | 설명 |
|---|---|
| `<SajuInputForm>` | 생년월일시·음양력·성별 입력 폼 |
| `<SajuProfileList>` | 저장된 만세력 목록 선택 (일주·이미지 표시) |
| `<SajuResultPanel>` | 만세력 전체 리포트 패널 |
| `<SajuDailyResultPanel>` | 오늘의 운세 결과 패널 |
| `<SajuTable>` | 4기둥 그리드 (천간·지지·십성·12운성·신살) |
| `<SajuHapChungPanel>` | 합충 탭 분석 (천간합·삼합·충·공망 등) |
| `<SajuWuxingPentagram>` | 오행 오각형 SVG |
| `<SajuWuxingDonutChart>` | 오행 도넛 차트 |
| `<SajuSipseongDonutChart>` | 십성 도넛 차트 |
| `<SajuStrengthChart>` | 신강·신약 8단계 차트 + 득령/득지/득시/득세 |
| `<SajuYongSinBadge>` | 용신·희신·기신 배지 |
| `<SajuDaeUnSlider>` | 대운 수평 슬라이더 |
| `<SajuYeonUnSlider>` | 연운 슬라이더 |
| `<SajuWolUnSlider>` | 월운 슬라이더 |
| `<SajuIlJinCalendar>` | 일진 달력 |

### `components/question/`

| 컴포넌트 | 설명 |
|---|---|
| `<QuestionConsultationResult>` | 한줄 상담 결과 카드 (프로필 + Q&A 블록) |

---

## 주요 Composables

| Composable | 설명 |
|---|---|
| `useSajuApi` | 백엔드 API 호출 래퍼 (calc, daily, question, share 등) |
| `useProfileSave` | 만세력 저장 상태 관리 (idle/loading/done/exists/error) |
| `useLoginStatePersist` | 로그인 이동 시 상태 localStorage 임시 저장 → 복귀 시 자동 복원 |
| `useGoToLogin` | 로그인 페이지 이동 (현재 경로 redirect 포함) |

---

## 애니메이션 규칙

- 페이지 진입 시 주요 섹션에 `animate-fade-up` 클래스 적용
- 순차 등장: `animate-delay-100` ~ `animate-delay-700`
- `ClientOnly` 내부 콘텐츠에 `animate-fade-up` 래퍼 필요 (hydration 후 동작)
