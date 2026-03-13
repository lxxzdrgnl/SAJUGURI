<script setup lang="ts">
import { ref, computed } from 'vue'
import type { SajuCalcResponse } from '~/types/saju'

const props = defineProps<{ saju: SajuCalcResponse }>()

const br  = computed(() => props.saju.branch_relations ?? {})
const gm  = computed(() => props.saju.gong_mang ?? { vacant_branches: [], affected_pillars: [] })

// ─── 탭 정의 ───────────────────────────────────────────────────────────────
type TabKey =
  | 'gung_seong' | 'cheon_gan_hap' | 'yuk_hap' | 'sam_hap' | 'bang_hap'
  | 'cheon_gan_chung' | 'chung' | 'gong_mang' | 'sam_hyeong' | 'pa' | 'yuk_hae' | 'won_jin'

const ALL_TABS: { key: TabKey; label: string; tip: string }[] = [
  { key: 'gung_seong',      label: '궁성',     tip: '기둥별 작용력 가중치입니다. 월지(×2.0)가 가장 강하고, 일간(×1.5), 나머지(×1.0) 순입니다.' },
  { key: 'cheon_gan_hap',   label: '천간합',   tip: '천간끼리 만나 새로운 오행으로 변화하는 관계입니다. 합화 여부는 주변 환경에 따라 결정됩니다.' },
  { key: 'yuk_hap',         label: '지지육합', tip: '두 지지가 짝을 이뤄 합화하는 관계입니다. 충이 있으면 합이 파괴될 수 있습니다.' },
  { key: 'sam_hap',         label: '지지삼합', tip: '세 지지가 모여 강한 오행 기운을 형성합니다. 세 기둥 중 두 개만 있어도 반합이 성립됩니다.' },
  { key: 'bang_hap',        label: '지지방합', tip: '같은 방위(봄·여름·가을·겨울)의 지지 셋이 모여 오행을 이루는 관계입니다.' },
  { key: 'cheon_gan_chung', label: '천간충',   tip: '천간끼리 충돌하는 관계입니다. 극(剋) 관계가 대립하여 불안정을 유발합니다.' },
  { key: 'chung',           label: '지지충',   tip: '정반대 지지끼리 충돌하는 관계입니다. 이동·변화·갈등을 의미하며 무조건 나쁜 것은 아닙니다.' },
  { key: 'gong_mang',       label: '공망',     tip: '일주 기준으로 작용력이 비어 있는 지지 2개입니다. 해당 기둥의 기운이 약해집니다.' },
  { key: 'sam_hyeong',      label: '형',       tip: '지지끼리 서로 해치는 관계입니다. 인사신·축술미·자형·오형 네 종류가 있습니다.' },
  { key: 'pa',              label: '파',       tip: '지지끼리 깨뜨리는 관계입니다. 충보다 약하나 관계·계획을 흔드는 작용을 합니다.' },
  { key: 'yuk_hae',         label: '해',       tip: '지지끼리 방해·막히는 관계입니다. 육합 성립을 가로막는 역할을 합니다.' },
  { key: 'won_jin',         label: '원진',     tip: '서로 미워하고 멀어지는 지지 관계입니다. 인연이 맺어져도 결국 등을 돌리게 됩니다.' },
]

const activeTab = ref<TabKey>('gung_seong')

// ─── 기둥 단축 ──────────────────────────────────────────────────────────────
type Pkey = 'year' | 'month' | 'day' | 'hour'
const PKEYS: Pkey[] = ['year', 'month', 'day', 'hour']
const PLABEL: Record<Pkey, string> = { year: '연', month: '월', day: '일', hour: '시' }

function pd(p: Pkey) {
  return props.saju[`${p}_pillar`] as any
}
const activePkeys = computed(() => PKEYS.filter(p => pd(p) !== null))
function findBranch(b: string): Pkey[] { return activePkeys.value.filter(p => pd(p).branch === b) }
function findStem(s: string): Pkey[]   { return activePkeys.value.filter(p => pd(p).stem   === s) }

// SAM_HYEONG 지지 목록
const SAM_HYEONG: Record<string, string[]> = {
  '인사신형': ['인', '사', '신'],
  '축술미형': ['축', '술', '미'],
  '자형':     ['자'],
  '오형':     ['오'],
}

// ─── 탭별 데이터 유무 ───────────────────────────────────────────────────────
function hasData(key: TabKey): boolean {
  if (key === 'gung_seong') return true
  if (key === 'gong_mang')  return gm.value.affected_pillars.length > 0
  const val = br.value[key]
  if (!val) return false
  if (Array.isArray(val)) return (val as any[]).length > 0
  if (typeof val === 'object') return Object.keys(val as object).length > 0
  return Boolean(val)
}

// ─── 엔트리 타입 ────────────────────────────────────────────────────────────
type Entry = {
  text: string         // "천간에 <b>병신합</b>이 있어요."
  stems:    Pkey[]     // 하이라이트할 기둥(천간)
  branches: Pkey[]     // 하이라이트할 기둥(지지)
  resultEl?: string    // 합화 오행
  broken?: boolean     // 육합 파괴 여부
}

// ─── Factory: 공통 빌더 함수 ────────────────────────────────────────────────

/** 지지 쌍 관계 빌더 — pillarDesc 추출 후 textFn에 위임 (충·파·해·원진 공용) */
function buildPairEntries(val: any[], textFn: (pair: string[], desc: string) => string): Entry[] {
  return val.map(v => {
    const pair: string[] = v.pair ?? v
    const pillars: Pkey[] = (v.pillars as string[] | undefined)?.map(p => p as Pkey)
      ?? pair.flatMap(b => findBranch(b))
    const desc = v.pillars ? `(${pillars.map(p => PLABEL[p] + '주').join('-')}) ` : ''
    return { text: textFn(pair, desc), stems: [], branches: pillars }
  })
}

/** 천간 관계 빌더 — pillars를 stems로 매핑 (천간합·천간충 공용) */
function buildStemEntries(val: any[], textFn: (v: any) => string, extraFn: (v: any) => Partial<Entry> = () => ({})): Entry[] {
  return val.map(v => ({
    text: textFn(v),
    stems: (v.pillars as string[]).map(p => p as Pkey),
    branches: [],
    ...extraFn(v),
  }))
}

/** 3지지 합 빌더 — branches 전체 하이라이트 (삼합·방합 공용) */
function buildGroupHapEntries(val: any): Entry[] {
  return (Array.isArray(val) ? val : [val]).map(item => ({
    text: `지지에 <b>${item.name ?? item.label ?? ''}</b>이 있어요.`,
    stems: [],
    branches: (item.branches ?? []).flatMap((b: string) => findBranch(b)),
    resultEl: item.element,
  }))
}

// ─── Registry (Strategy Pattern): TabKey → Entry 빌더 매핑 ─────────────────

type EntryBuilder = (val: any) => Entry[]

const ENTRY_BUILDERS: Partial<Record<TabKey, EntryBuilder>> = {
  cheon_gan_hap:   v => buildStemEntries(v, x => `천간에 <b>${x.name ?? x.stems?.join('')}</b>이 있어요.`, x => ({ resultEl: x.result_element })),
  cheon_gan_chung: v => buildStemEntries(v, x => `천간에 <b>${x.name}</b>이 있어요.`),
  yuk_hap: val => (val as any[]).map(v => {
    const pair: string[] = v.pair ?? []
    const pillars: Pkey[] = (v.pillars as string[] | undefined)?.map(p => p as Pkey) ?? pair.flatMap(b => findBranch(b))
    const desc = pillars.length ? `(${pillars.map(p => PLABEL[p] + '주').join('-')}) ` : ''
    return { text: `${desc}지지에 <b>${pair.join('')}육합</b>이 있어요.`, stems: [], branches: pillars, resultEl: v.element, broken: v.is_effective === false }
  }),
  sam_hap:    v => buildGroupHapEntries(v),
  bang_hap:   v => buildGroupHapEntries(v),
  sam_hyeong: (val: string[]) => val.map(name => ({
    text: `지지에 <b>${name}</b>이 있어요.`,
    stems: [],
    branches: (SAM_HYEONG[name] ?? []).flatMap(b => findBranch(b)),
  })),
  chung:   v => buildPairEntries(v, (p, d) => `${d}지지에 <b>${p.join('충')}</b>이 있어요.`),
  yuk_hae: v => buildPairEntries(v, (p, d) => `${d}지지에 <b>${p.join('·')}해</b>가 있어요.`),
  pa:      v => buildPairEntries(v, (p, d) => `${d}지지에 <b>${p.join('·')}파</b>가 있어요.`),
  won_jin: v => buildPairEntries(v, (p, d) => `${d}지지에 <b>${p.join('·')}원진</b>이 있어요.`),
}

// ─── entries computed ────────────────────────────────────────────────────────

const entries = computed<Entry[]>(() => {
  const key = activeTab.value
  if (key === 'gung_seong') return []

  if (key === 'gong_mang') {
    const vacant = gm.value.vacant_branches as string[]
    return (gm.value.affected_pillars as string[]).map(p => {
      const pkey = p as Pkey
      return {
        text: `<b>${PLABEL[pkey]}주 지지 ${pd(pkey)?.branch}</b>가 공망이에요. (공망 지지: ${vacant.join(', ')})`,
        stems: [],
        branches: [pkey],
      }
    })
  }

  const val = br.value[key]
  if (!val) return []
  return ENTRY_BUILDERS[key]?.(val) ?? []
})

// ─── 궁성 가중치 표시 ──────────────────────────────────────────────────────
const PALACE_INFO = [
  { pkey: 'hour'  as Pkey, stemW: '×1.0', branchW: '×0.8' },
  { pkey: 'day'   as Pkey, stemW: '×1.5', branchW: '×1.0' },
  { pkey: 'month' as Pkey, stemW: '×1.0', branchW: '×2.0' },
  { pkey: 'year'  as Pkey, stemW: '×1.0', branchW: '×1.0' },
]
</script>

<template>
  <div class="hap-panel">

    <!-- ── 탭 행 ─────────────────────────────────────────────────────────── -->
    <div class="tab-row">
      <button
        v-for="tab in ALL_TABS"
        :key="tab.key"
        class="tab-btn"
        :class="{
          'tab-active':    activeTab === tab.key,
          'tab-has-data':  activeTab !== tab.key && hasData(tab.key),
          'tab-no-data':   activeTab !== tab.key && !hasData(tab.key),
        }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ── 패널 본문 ─────────────────────────────────────────────────────── -->
    <div class="panel-body">

      <!-- 궁성 특별 탭 -->
      <template v-if="activeTab === 'gung_seong'">
        <p class="gung-desc">
          궁성의 위치에 따라 오행의 비율을 다르게 적용합니다.<br>
          <span style="color: var(--text-muted);">월지 &gt; 일간 &gt; 시지/연주 &gt; 천간 순서로 작용력이 다릅니다.</span>
        </p>

        <!-- 기둥 가중치 그리드 -->
        <div class="pillar-grid">
          <div v-for="info in PALACE_INFO" :key="info.pkey" class="pillar-col">
            <div class="pillar-label-top">{{ PLABEL[info.pkey] }}주</div>
            <div class="pillar-box pillar-box-stem" :class="pd(info.pkey) ? '' : 'box-null'">
              <span class="pbox-main">{{ pd(info.pkey)?.stem ?? '—' }}</span>
              <span class="pbox-hanja">{{ pd(info.pkey)?.stem_hanja ?? '' }}</span>
              <span class="pbox-weight">{{ info.stemW }}</span>
            </div>
            <div class="pillar-box pillar-box-branch" :class="pd(info.pkey) ? '' : 'box-null'">
              <span class="pbox-main">{{ pd(info.pkey)?.branch ?? '—' }}</span>
              <span class="pbox-hanja">{{ pd(info.pkey)?.branch_hanja ?? '' }}</span>
              <span class="pbox-weight" :class="info.pkey === 'month' ? 'weight-strong' : ''">{{ info.branchW }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- 일반 탭 -->
      <template v-else>
        <!-- 탭 설명 -->
        <p class="tab-desc">{{ ALL_TABS.find(t => t.key === activeTab)?.tip }}</p>

        <!-- 데이터 없음 -->
        <div v-if="!hasData(activeTab)" class="empty-msg">
          해당하는 {{ ALL_TABS.find(t => t.key === activeTab)?.label }}이 없습니다.
        </div>

        <!-- 엔트리 목록 -->
        <div v-else class="entry-list">
          <div v-for="(entry, idx) in entries" :key="idx" class="entry-item">
            <!-- 설명 텍스트 -->
            <p class="entry-text" v-html="entry.text" />

            <!-- 파괴 뱃지 -->
            <span v-if="entry.broken" class="broken-badge">충으로 합 파괴됨</span>

            <!-- 합화 오행 -->
            <span v-if="entry.resultEl && !entry.broken" class="result-el-badge"
                  :style="`color: ${elColor(entry.resultEl)}; border-color: ${elColor(entry.resultEl)}33; background: ${elColor(entry.resultEl)}11;`">
              → {{ entry.resultEl }}화(化)
            </span>

            <!-- 미니 기둥 그리드 -->
            <div class="pillar-grid">
              <div v-for="pkey in activePkeys" :key="pkey" class="pillar-col">
                <div class="pillar-label-top">{{ PLABEL[pkey] }}주</div>
                <!-- 천간 박스 -->
                <div
                  class="pillar-box pillar-box-stem"
                  :class="entry.stems.includes(pkey) ? 'box-highlight' : 'box-normal'"
                >
                  <span class="pbox-main">{{ pd(pkey)?.stem ?? '—' }}</span>
                  <span class="pbox-hanja">{{ pd(pkey)?.stem_hanja ?? '' }}</span>
                </div>
                <!-- 지지 박스 -->
                <div
                  class="pillar-box pillar-box-branch"
                  :class="entry.branches.includes(pkey) ? 'box-highlight' : 'box-normal'"
                >
                  <span class="pbox-main">{{ pd(pkey)?.branch ?? '—' }}</span>
                  <span class="pbox-hanja">{{ pd(pkey)?.branch_hanja ?? '' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* ── 패널 래퍼 ── */
.hap-panel {
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
}

/* ── 탭 행 ── */
.tab-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--surface-3);
  background: var(--surface-2);
}

.tab-btn {
  padding: 5px 12px;
  border-radius: 999px;
  font-size: var(--fs-label);
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-active {
  background: var(--accent);
  color: var(--surface-1);
  border-color: var(--accent);
}

.tab-has-data {
  background: color-mix(in srgb, var(--accent) 8%, var(--surface-1));
  color: var(--accent);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
}

.tab-has-data:hover {
  background: color-mix(in srgb, var(--accent) 15%, var(--surface-1));
  border-color: var(--accent);
}

.tab-no-data {
  background: transparent;
  color: var(--text-muted);
  border-color: var(--border-subtle);
}

.tab-no-data:hover {
  color: var(--text-muted);
  border-color: var(--border-default);
}

/* ── 본문 ── */
.panel-body {
  padding: 16px 14px;
}

/* ── 궁성 안내 ── */
.gung-desc {
  font-size: var(--fs-label);
  color: var(--text-secondary);
  margin-bottom: 14px;
  line-height: 1.7;
}

/* ── 탭 설명 ── */
.tab-desc {
  font-size: var(--fs-label);
  color: var(--text-muted);
  line-height: 1.6;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--surface-3);
  margin-bottom: 4px;
}

/* ── 빈 메시지 ── */
.empty-msg {
  font-size: var(--fs-label);
  color: var(--text-muted);
  padding: 12px 0;
}

/* ── 엔트리 ── */
.entry-list { display: flex; flex-direction: column; gap: 20px; }

.entry-item { display: flex; flex-direction: column; gap: 8px; }

.entry-text {
  font-size: var(--fs-label);
  color: var(--text-secondary);
  line-height: 1.5;
}
.entry-text :deep(b) { color: var(--text-primary); font-weight: 700; }

.broken-badge {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--el-화) 8%, transparent);
  color: var(--el-화);
  border: 1px solid color-mix(in srgb, var(--el-화) 20%, transparent);
}

.result-el-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 9px;
  border-radius: 4px;
  border: 1px solid;
}

/* ── 기둥 그리드 ── */
.pillar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(52px, 1fr));
  gap: 6px;
}

.pillar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.pillar-label-top {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

/* ── 기둥 박스 공통 ── */
.pillar-box {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 8px 4px 6px;
  border: 1px solid;
  position: relative;
  min-height: 52px;
  transition: all 0.15s;
}

/* 일반 (비하이라이트) */
.box-normal {
  background: var(--surface-1);
  border-color: var(--border-subtle);
}

/* 시주 미입력 */
.box-null {
  background: var(--surface-2);
  border-color: var(--border-subtle);
  opacity: 0.5;
}

/* 하이라이트 — 브랜드 액센트 */
.box-highlight {
  background: color-mix(in srgb, var(--accent) 85%, white);
  border-color: var(--accent);
}
.box-highlight .pbox-main  { color: #ffffff; }
.box-highlight .pbox-hanja { color: color-mix(in srgb, #ffffff 70%, transparent); }

/* 기둥 박스 내부 텍스트 */
.pbox-main {
  font-family: var(--font-ganji);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.pbox-hanja {
  font-family: var(--font-ganji);
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-top: 2px;
}

.pbox-weight {
  position: absolute;
  bottom: 3px;
  right: 4px;
  font-size: 9px;
  color: var(--text-muted);
  font-weight: 600;
}

.weight-strong {
  color: var(--el-화);
  font-weight: 700;
}

/* ── 반응형 ── */
@media (max-width: 480px) {
  .pbox-main  { font-size: 1rem; }
  .pbox-hanja { font-size: 0.6rem; }
  .pillar-box { padding: 6px 2px 4px; min-height: 44px; }
}
</style>
