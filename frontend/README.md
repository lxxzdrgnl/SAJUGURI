# Frontend — Vue.js 3 + Nuxt.js

## 개요

사주 입력부터 만세력 리포트까지 모든 UI를 담당하는 Nuxt.js 3 앱입니다.

### 주요 화면

| 화면 | 설명 |
|---|---|
| 입력 폼 | 이름·출생지(도시 검색)·생년월일·시각·성별 입력 |
| 만세력 리포트 | 사주팔자 테이블, 합충 분석, 오행 차트, 대운·연운·월운 슬라이더, 일진 달력 |

### 입력 폼 기능

- **도시 검색**: 한국어/영문 통합 검색 → 백엔드 `GET /api/cities` 호출 (geonamescache 기반)
- **진태양시 보정 미리보기**: 도시 선택 시 보정 분수 + 적용 시각 + 시시(時辰) 실시간 표시
- **생년월일·시각 통합 입력**: `YYYY / MM / DD · HH : MM` 한 줄, 자동 포커스 이동·백스페이스 탐색
- **양력/음력/윤달 3-pill 토글**: 항상 표시, 양력 선택 시 윤달 비활성화

---

## 실행

```bash
cd frontend

# 의존성 설치
pnpm install

# 환경변수 설정
cp .env.example .env
# NUXT_PUBLIC_API_BASE=http://localhost:8000

# 개발 서버 실행
pnpm dev
```

개발 서버: `http://localhost:3000`
백엔드 `/api/**` 요청은 `NUXT_PUBLIC_API_BASE`로 자동 프록시됩니다.

---

## 빌드

```bash
pnpm build
pnpm preview
```

---

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | 백엔드 API 주소 |

---

## 기술 스택

| 항목 | 기술 |
|---|---|
| Framework | Nuxt.js 3 |
| UI | Vue.js 3 (Composition API) |
| 상태 관리 | Pinia |
| 스타일 | Tailwind CSS |
| 차트 | Chart.js |
| 패키지 매니저 | pnpm |

---

## 주요 컴포넌트

| 컴포넌트 | 설명 |
|---|---|
| `components/saju/InputForm.vue` | 사주 입력 폼 (도시 검색, 날짜·시각, 성별) |
| `components/saju/SajuTable.vue` | 4기둥 그리드 (천간·지지·십성·12운성·신살) |
| `components/saju/HapChungPanel.vue` | 합충 탭 분석 |
| `components/saju/WuxingPentagram.vue` | 오행 오각형 SVG |
| `components/saju/WuxingDonutChart.vue` | 오행 도넛 차트 |
| `components/saju/SipseongDonutChart.vue` | 십성 도넛 차트 |
| `components/saju/StrengthBar.vue` | 신강·신약 8단계 바 |
| `components/saju/YongSinBadge.vue` | 용신·희신·기신 배지 |
| `components/saju/DaeUnSlider.vue` | 대운 수평 슬라이더 |
| `components/saju/YeonUnSlider.vue` | 연운 슬라이더 |
| `components/saju/WolUnSlider.vue` | 월운 슬라이더 |
| `components/saju/IlJinCalendar.vue` | 일진 달력 |

---

## 사용된 오픈소스 라이브러리

| 패키지 | 라이선스 | 용도 |
|---|---|---|
| [Nuxt.js 3](https://github.com/nuxt/nuxt) | MIT | SSR/SSG 프레임워크 |
| [Vue.js 3](https://github.com/vuejs/core) | MIT | UI 프레임워크 |
| [Pinia](https://github.com/vuejs/pinia) | MIT | 상태 관리 |
| [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) | MIT | CSS 유틸리티 |
| [Chart.js](https://github.com/chartjs/Chart.js) | MIT | 오행·십성 도넛 차트 |
| [pnpm](https://github.com/pnpm/pnpm) | MIT | 패키지 매니저 |
