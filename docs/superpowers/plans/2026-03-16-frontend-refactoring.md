# Frontend Refactoring Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate duplicated code across the Vue/Nuxt frontend by consolidating ganji constants, utility functions, shared components, and localStorage keys into single-source-of-truth modules.

**Architecture:** Extract repeated logic into `utils/`, `components/ui/`, and `composables/`. Replace all inline duplicates with imports. No behavior changes — pure refactoring.

**Tech Stack:** Vue 3, Nuxt 3, TypeScript, Pinia, Tailwind CSS

---

## Chunk A: Ganji Constants + Utility Functions → `utils/ganji.ts`

**Files:**
- Create: `frontend/utils/ganji.ts`
- Modify: `frontend/pages/index.vue`
- Modify: `frontend/pages/my-profiles.vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/components/saju/DailyResultPanel.vue`

### Task A1: Create `utils/ganji.ts`

- [ ] Create `frontend/utils/ganji.ts` with all ganji constants and helpers:

```typescript
// frontend/utils/ganji.ts

export const STEMS = ['갑','을','병','정','무','기','경','신','임','계']
export const BRANCHES = ['자','축','인','묘','진','사','오','미','신','유','술','해']

export const STEM_HANJA: Record<string, string> = {
  '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊',
  '기':'己','경':'庚','신':'辛','임':'壬','계':'癸'
}
export const BRANCH_HANJA: Record<string, string> = {
  '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳',
  '오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥'
}
export const STEM_COLOR: Record<string, string> = {
  '갑':'청','을':'청','병':'붉은','정':'붉은','무':'황',
  '기':'황','경':'흰','신':'흰','임':'검은','계':'검은'
}
export const STEM_ELEMENT: Record<string, string> = {
  '갑':'목','을':'목','병':'화','정':'화','무':'토',
  '기':'토','경':'금','신':'금','임':'수','계':'수'
}
export const BRANCH_ELEMENT: Record<string, string> = {
  '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화',
  '오':'화','미':'토','신':'금','유':'금','술':'토','해':'수'
}
export const BRANCH_ANIMAL: Record<string, string> = {
  '자':'쥐','축':'소','인':'호랑이','묘':'토끼','진':'용','사':'뱀',
  '오':'말','미':'양','신':'원숭이','유':'닭','술':'개','해':'돼지'
}

export const TEN_GOD_ELEMENT: Record<string, string> = {
  '비견':'목','겁재':'목','식신':'화','상관':'화',
  '편재':'토','정재':'토','편관':'금','정관':'금',
  '편인':'수','정인':'수'
}

export const KOREAN_DAYS = ['일','월','화','수','목','금','토'] as const
export const KOREAN_MONTHS = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'] as const

/** 기준일 1900-01-01 = 갑술일 (stemIdx=0, branchIdx=10) 기준 오늘 일주 계산 */
export function calcTodayIlju(): { stem: string; branch: string } {
  const base = new Date(1900, 0, 1)
  const today = new Date()
  const days = Math.floor((today.getTime() - base.getTime()) / 86400000)
  const stemIdx = ((days % 10) + 10) % 10
  const branchIdx = ((days + 10) % 12 + 12) % 12
  return { stem: STEMS[stemIdx], branch: BRANCHES[branchIdx] }
}

/** "2026년 3월 16일 (일)" 형식 */
export function formatTodayLabel(): string {
  const d = new Date()
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${KOREAN_DAYS[d.getDay()]})`
}

/** 일주 한자 표기: "庚午" */
export function formatIljuHanja(stem: string | null | undefined, branch: string | null | undefined): string {
  if (!stem || !branch) return ''
  return `${STEM_HANJA[stem] ?? stem}${BRANCH_HANJA[branch] ?? branch}`
}

/** 일주 색상 레이블: "흰 말" */
export function formatIljuLabel(stem: string | null | undefined, branch: string | null | undefined): string {
  if (!stem || !branch) return ''
  return `${STEM_COLOR[stem] ?? ''} ${BRANCH_ANIMAL[branch] ?? ''}`
}

/** 일주 색상 CSS 변수 */
export function iljuColor(stem: string | null | undefined): string {
  if (!stem) return 'var(--text-secondary)'
  return `var(--el-${STEM_ELEMENT[stem] ?? ''})`
}
```

- [ ] Verify file saved correctly.

### Task A2: Update `pages/index.vue`

- [ ] Remove locally defined STEMS, BRANCHES, STEM_HANJA, BRANCH_HANJA, STEM_COLOR, STEM_ELEMENT, BRANCH_ELEMENT, BRANCH_ANIMAL, KOREAN_DAYS constants.
- [ ] Remove locally defined `calcTodayIlju()`, `formatTodayLabel()` (or inline equivalents).
- [ ] Add import at top of `<script setup>`:
```typescript
import { STEMS, BRANCHES, STEM_HANJA, BRANCH_HANJA, STEM_COLOR, STEM_ELEMENT, BRANCH_ELEMENT, BRANCH_ANIMAL, KOREAN_DAYS, calcTodayIlju, formatTodayLabel, formatIljuHanja, formatIljuLabel, iljuColor } from '~/utils/ganji'
```
- [ ] Verify page still renders correctly in browser (or check no TS errors).

### Task A3: Update `pages/my-profiles.vue`

- [ ] Remove locally defined STEM_HANJA, BRANCH_HANJA, STEM_COLOR, BRANCH_ANIMAL, STEM_ELEMENT and `iljuHanja()`, `iljuLabel()` functions.
- [ ] Import from `~/utils/ganji`.
- [ ] Replace `iljuHanja(p)` calls → `formatIljuHanja(p.day_stem, p.day_branch)`.
- [ ] Replace `iljuLabel(p)` calls → `formatIljuLabel(p.day_stem, p.day_branch)`.

### Task A4: Update `pages/daily/index.vue`

- [ ] Remove all locally defined ganji constants (STEMS, BRANCHES, etc.).
- [ ] Import from `~/utils/ganji`.
- [ ] Replace `todayLabel` inline computation → `formatTodayLabel()`.
- [ ] Replace `todayIlju` inline computation → `calcTodayIlju()`.

### Task A5: Update `components/saju/DailyResultPanel.vue`

- [ ] Remove locally defined STEMS, BRANCHES, STEM_ELEMENT, BRANCH_ELEMENT (lines 6-25).
- [ ] Import from `~/utils/ganji`.

---

## Chunk B: Element Color Consolidation → `utils/elementColor.ts`

**Files:**
- Modify: `frontend/utils/elementColor.ts` (already exists — add `iljuColor` re-export)
- Modify: `frontend/pages/index.vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/components/saju/DailyResultPanel.vue`
- Modify: `frontend/components/saju/Table.vue`

The `elColor` function already exists in `utils/elementColor.ts`. The issue is files define their own local copies instead of importing.

### Task B1: Verify `utils/elementColor.ts` has correct `elColor` signature

- [ ] Read `frontend/utils/elementColor.ts`.
- [ ] Ensure `elColor(el: string): string` is exported.
- [ ] If `iljuColor` is not yet exported here, import and re-export it from `utils/ganji.ts` (or define inline — pick one canonical location).

### Task B2: Remove duplicate `elColor`/`iljuColor` definitions from other files

- [ ] `pages/daily/index.vue`: Remove local `elColor()` definition, import from `~/utils/elementColor`.
- [ ] `components/saju/DailyResultPanel.vue`: Remove local `elColor()` definition, import from `~/utils/elementColor`.
- [ ] `components/saju/Table.vue`: If using local `ec()` that wraps `elColor`, import `elColor` directly.
- [ ] Verify no TS errors after changes.

---

## Chunk C: `LoadingSpinner` Component → `components/ui/LoadingSpinner.vue`

**Files:**
- Create: `frontend/components/ui/LoadingSpinner.vue`
- Modify: `frontend/pages/index.vue`
- Modify: `frontend/pages/profile.vue`
- Modify: `frontend/pages/share/[token].vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/pages/daily/share/[token].vue`
- Modify: `frontend/pages/my-profiles.vue`

The SVG spinner is duplicated in 6+ files. The exact markup is:
```html
<svg class="animate-spin w-8 h-8" viewBox="0 0 40 40" fill="none">
  <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
  <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
</svg>
```

### Task C1: Create `components/ui/LoadingSpinner.vue`

- [ ] Create `frontend/components/ui/LoadingSpinner.vue`:

```vue
<template>
  <svg :class="['animate-spin', sizeClass]" viewBox="0 0 40 40" fill="none">
    <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
    <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
  </svg>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })
const sizeClass = computed(() => ({ sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }[props.size]))
</script>
```

### Task C2: Replace spinner markup in all 6 pages

- [ ] `pages/index.vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] `pages/profile.vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] `pages/share/[token].vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] `pages/daily/index.vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] `pages/daily/share/[token].vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] `pages/my-profiles.vue`: Replace SVG spinner → `<LoadingSpinner />`.
- [ ] Nuxt auto-imports components — no explicit import needed.

---

## Chunk D: `ProfileCardItem` Component → `components/saju/ProfileCardItem.vue`

**Files:**
- Create: `frontend/components/saju/ProfileCardItem.vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/pages/my-profiles.vue`
- Modify: `frontend/pages/index.vue`

Profile card rendering is duplicated across at least 3 pages with slight variations.

### Task D1: Read profile card markup in each page

- [ ] Read `pages/daily/index.vue` lines 357-395 to see daily profile card structure.
- [ ] Read `pages/my-profiles.vue` lines 153-197 to see profile list item structure.
- [ ] Read `pages/index.vue` lines 167-192 to see representative profile card.
- [ ] Note common vs varying parts.

### Task D2: Create `components/saju/ProfileCardItem.vue`

Based on findings from D1, create a unified component. Expected interface:

```vue
<template>
  <!-- Profile name, ilju hanja badge, birth info, optional slot for actions -->
</template>

<script setup lang="ts">
interface ProfileItem {
  id: number
  name: string
  birth_date: string
  birth_time?: string | null
  gender: string
  calendar: string
  day_stem?: string | null
  day_branch?: string | null
}
const props = defineProps<{
  profile: ProfileItem
  active?: boolean
}>()
</script>
```

### Task D3: Replace inline profile card markup in pages

- [ ] Replace inline profile card in `pages/daily/index.vue` with `<ProfileCardItem>`.
- [ ] Replace inline profile card in `pages/my-profiles.vue` with `<ProfileCardItem>`.
- [ ] Replace inline profile card in `pages/index.vue` with `<ProfileCardItem>`.
- [ ] Add action slots where needed (delete button, set-representative button, etc.).

---

## Chunk E: localStorage Key Consolidation → `utils/storageKeys.ts`

**Files:**
- Create: `frontend/utils/storageKeys.ts`
- Modify: `frontend/stores/auth.ts`
- Modify: `frontend/composables/useGoToLogin.ts`
- Modify: `frontend/pages/login.vue`
- Modify: `frontend/pages/profile.vue`
- Modify: `frontend/pages/auth/callback.vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/components/saju/ResultPanel.vue`

### Task E1: Audit all localStorage key strings

- [ ] Run: `grep -r "localStorage" frontend/ --include="*.vue" --include="*.ts" -n` to find all usages.
- [ ] List all string keys found.

### Task E2: Create `utils/storageKeys.ts`

- [ ] Create `frontend/utils/storageKeys.ts`:

```typescript
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  SAJU_PENDING_STATE: 'saju_pending_state',
  SAJU_PENDING_SAVE: 'saju_pending_save',
  SAJU_LOGIN_REDIRECT: 'saju_login_redirect',
  DAILY_PENDING_INPUT: 'daily_pending_input',
} as const

export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS]
```

### Task E3: Replace string literals with STORAGE_KEYS constants

- [ ] `stores/auth.ts`: Replace `'auth_token'`, `'refresh_token'` → `STORAGE_KEYS.AUTH_TOKEN`, `STORAGE_KEYS.REFRESH_TOKEN`.
- [ ] `composables/useGoToLogin.ts`: Replace string literals.
- [ ] `pages/login.vue`: Replace string literals.
- [ ] `pages/profile.vue`: Replace string literals.
- [ ] `pages/auth/callback.vue`: Replace string literals.
- [ ] `pages/daily/index.vue`: Replace string literals.
- [ ] `components/saju/ResultPanel.vue`: Replace string literals.
- [ ] Verify no string literals remain (re-run grep to confirm).

---

## Chunk F: API Endpoints Consolidation + `useApiBase` Composable

**Files:**
- Create: `frontend/utils/apiEndpoints.ts`
- Create: `frontend/composables/useApiBase.ts`
- Modify: `frontend/composables/useSajuApi.ts`
- Modify: `frontend/composables/useProfileSave.ts`
- Modify: `frontend/pages/profile.vue`
- Modify: `frontend/pages/daily/index.vue`
- Modify: `frontend/stores/auth.ts`

### Task F1: Create `utils/apiEndpoints.ts`

- [ ] Create `frontend/utils/apiEndpoints.ts`:

```typescript
export const API = {
  SAJU_CALC: '/api/saju/calc',
  SAJU_DAILY: '/api/saju/daily',
  SAJU_WOL_UN: '/api/saju/wol-un',
  SAJU_IL_JIN: '/api/saju/il-jin',
  PROFILES: '/api/profiles',
  PROFILES_REPRESENTATIVE: '/api/profiles/representative',
  profile: (id: number) => `/api/profiles/${id}`,
  SHARE: (token: string) => `/api/share/${token}`,
  SHARE_DAILY: (token: string) => `/api/share/daily/${token}`,
  AUTH_GOOGLE: '/api/auth/google',
  AUTH_GOOGLE_CALLBACK: '/api/auth/google/callback',
  AUTH_ME: '/api/auth/me',
  AUTH_REFRESH: '/api/auth/refresh',
  AUTH_LOGOUT: '/api/auth/logout',
} as const
```

### Task F2: Create `composables/useApiBase.ts`

- [ ] Create `frontend/composables/useApiBase.ts`:

```typescript
export function useApiBase(): string {
  const config = useRuntimeConfig()
  return config.public.apiBase as string
}
```

### Task F3: Update composables and pages to use centralized endpoints

- [ ] `composables/useSajuApi.ts`: Replace inline path strings with `API.*` constants.
- [ ] `composables/useProfileSave.ts`: Replace inline path strings; use `useApiBase()`.
- [ ] `pages/profile.vue`: Replace inline endpoint strings.
- [ ] `pages/daily/index.vue`: Replace inline endpoint strings.
- [ ] `stores/auth.ts`: Replace inline endpoint strings.
- [ ] Verify no hardcoded `/api/...` strings remain outside `apiEndpoints.ts`.

---

## Chunk G: Final Verification

### Task G1: TypeScript check

- [ ] Run: `cd frontend && npx nuxi typecheck` (or `npx tsc --noEmit`).
- [ ] Fix any type errors introduced by refactoring.

### Task G2: Manual smoke test

- [ ] Start dev server: `cd frontend && pnpm dev` (or use existing running server).
- [ ] Visit home page — profile card and spinner render correctly.
- [ ] Visit `/daily` — ganji display works, spinner shows during loading.
- [ ] Visit `/my-profiles` — profile list renders correctly with ilju hanja.
- [ ] Confirm localStorage operations work (login/save flow).

### Task G3: Grep for remaining duplication

- [ ] Run: `grep -r "animate-spin" frontend/ --include="*.vue" -l` — should be 0 results (only in LoadingSpinner.vue).
- [ ] Run: `grep -r "STEM_HANJA\|BRANCH_HANJA\|STEM_COLOR\|BRANCH_ANIMAL" frontend/ --include="*.vue" -l` — should be 0 (only in ganji.ts).
- [ ] Run: `grep -r "'auth_token'\|'refresh_token'\|'saju_pending" frontend/ --include="*.vue" --include="*.ts" -l` — should be 0 (only in storageKeys.ts).

---

## Additional Opportunities (Lower Priority)

These were identified but are lower priority than the above chunks:

- **State type definitions** → `types/states.ts`: `SaveState`, `DailyStep` etc. (cosmetic improvement)
- **`useAsyncOperation` composable**: Generic loading/done/error state helper (3 places use identical pattern)
- **Error card styling**: Consistent CSS class instead of inline rgba styles
- **GYEOK_DESC and other description objects**: Move to `data/descriptions.ts`
- **Inline style consolidation**: Convert remaining inline styles to Tailwind classes

These can be addressed in a follow-up pass after the main 6 chunks above are done.
