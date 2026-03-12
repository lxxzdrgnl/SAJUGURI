<script setup lang="ts">
import type { SajuCalcResponse, SinSal } from '~/types/saju'

const props = defineProps<{ data: SajuCalcResponse }>()

// 시주 → 일주 → 월주 → 연주 (좌→우). 시주 null이면 "—" 표시
const pillars = [
  { key: 'hour_pillar'  as const, label: '시주', colLabel: '생시', loc: 'hour' },
  { key: 'day_pillar'   as const, label: '일주', colLabel: '생일', loc: 'day'  },
  { key: 'month_pillar' as const, label: '월주', colLabel: '생월', loc: 'month' },
  { key: 'year_pillar'  as const, label: '연주', colLabel: '생년', loc: 'year'  },
]

const jijangganKeys = pillars.map(p => p.loc)
const pillarLocKeys = pillars.map(p => p.loc)

function ec(el: string) { return elColor(el) }

const tenGodElement: Record<string, string> = {
  '비견': '목', '겁재': '목', '식신': '화', '상관': '화',
  '편재': '토', '정재': '토', '편관': '금', '정관': '금',
  '편인': '수', '정인': '수',
}
function tenGodColor(tg: string) { return ec(tenGodElement[tg] ?? '') }

function isDay(i: number) { return i === 1 }
function sign(p: { yin_yang: string }) { return p.yin_yang === '양' ? '+' : '-' }

// 기둥별 신살 필터
function pillarSinSals(pillarIdx: number): SinSal[] {
  const key = pillarLocKeys[pillarIdx]
  return (props.data.sin_sals ?? []).filter(s =>
    s.location?.some(loc => loc === key || loc.startsWith(key))
  )
}

function sinSalSignColor(type: string) {
  if (type === 'lucky')                        return `color: var(--color-good);`
  if (type === 'unlucky' || type === 'warning') return `color: var(--color-bad);`
  return `color: var(--text-muted);`
}
</script>

<template>
  <div class="saju-table-wrap">
    <div class="table-block">
      <div class="overflow-x-auto scrollbar-thin">
        <table class="saju-table">
          <colgroup>
            <col class="col-label">
            <col><col><col><col>
          </colgroup>

          <!-- 열 헤더 -->
          <thead>
            <tr class="header-row">
              <th class="cell-label"></th>
              <th v-for="(p, i) in pillars" :key="p.key"
                  class="cell-head" :class="{ 'day-col': isDay(i) }">
                <span :style="isDay(i) ? `color: ${ec('화')};` : 'color: var(--text-muted);'">
                  {{ p.colLabel }}
                </span>
              </th>
            </tr>
          </thead>

          <tbody>
            <!-- ── 천간 ── -->
            <tr>
              <td class="cell-label row-label">천간</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-stem'"
                  class="cell-data cell-ganji" :class="{ 'day-col': isDay(i) }">
                <div v-if="data[p.key]" class="ganji-wrap">
                  <div class="ganji-pair">
                    <span class="ganji-main" :style="`color: ${ec(data[p.key]!.stem_element)};`">
                      {{ data[p.key]!.stem }}
                    </span>
                    <span class="ganji-hanja" :style="`color: ${ec(data[p.key]!.stem_element)};`">
                      {{ data[p.key]!.stem_hanja }}
                    </span>
                  </div>
                  <span class="el-sign" :style="`color: ${ec(data[p.key]!.stem_element)};`">
                    {{ sign(data[p.key]!) }}{{ data[p.key]!.stem_element }}
                  </span>
                </div>
                <span v-else class="null-dash">—</span>
              </td>
            </tr>

            <!-- 천간 십성 -->
            <tr>
              <td class="cell-label row-label">십성</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-stem-tg'"
                  class="cell-data cell-sm" :class="{ 'day-col': isDay(i) }">
                <span v-if="data[p.key]?.stem_ten_god" class="font-medium"
                      :style="`color: ${tenGodColor(data[p.key]!.stem_ten_god)};`">
                  {{ data[p.key]!.stem_ten_god }}
                </span>
                <span v-else style="color: var(--border-subtle);">—</span>
              </td>
            </tr>

            <!-- ── 지지 ── -->
            <tr>
              <td class="cell-label row-label">지지</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-branch'"
                  class="cell-data cell-ganji" :class="{ 'day-col': isDay(i) }">
                <div v-if="data[p.key]" class="ganji-wrap">
                  <div class="ganji-pair">
                    <span class="ganji-main" :style="`color: ${ec(data[p.key]!.branch_element)};`">
                      {{ data[p.key]!.branch }}
                    </span>
                    <span class="ganji-hanja" :style="`color: ${ec(data[p.key]!.branch_element)};`">
                      {{ data[p.key]!.branch_hanja }}
                    </span>
                  </div>
                  <span class="el-sign" :style="`color: ${ec(data[p.key]!.branch_element)};`">
                    {{ sign(data[p.key]!) }}{{ data[p.key]!.branch_element }}
                  </span>
                </div>
                <span v-else class="null-dash">—</span>
              </td>
            </tr>

            <!-- 지지 십성 -->
            <tr>
              <td class="cell-label row-label">십성</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-branch-tg'"
                  class="cell-data cell-sm" :class="{ 'day-col': isDay(i) }">
                <span v-if="data[p.key]?.branch_ten_god" class="font-medium"
                      :style="`color: ${tenGodColor(data[p.key]!.branch_ten_god)};`">
                  {{ data[p.key]!.branch_ten_god }}
                </span>
                <span v-else style="color: var(--border-subtle);">—</span>
              </td>
            </tr>

            <!-- 지장간 -->
            <tr>
              <td class="cell-label row-label">지장간</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-jjg'"
                  class="cell-data cell-sm" :class="{ 'day-col': isDay(i) }">
                <span v-if="data[p.key]" style="color: var(--text-muted); letter-spacing: 0.05em;">
                  {{ (data.ji_jang_gan?.[jijangganKeys[i]] ?? []).join('') }}
                </span>
                <span v-else style="color: var(--border-subtle);">—</span>
              </td>
            </tr>

            <!-- 12운성 -->
            <tr>
              <td class="cell-label row-label">12운성</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-wun'"
                  class="cell-data cell-sm" :class="{ 'day-col': isDay(i) }">
                <span v-if="data[p.key]" class="font-medium" style="color: var(--el-목);">
                  {{ data[p.key]!.twelve_wun }}
                </span>
                <span v-else style="color: var(--border-subtle);">—</span>
              </td>
            </tr>

            <!-- 신살 (기둥별 필터링) -->
            <tr>
              <td class="cell-label row-label">신살</td>
              <td v-for="(p, i) in pillars" :key="p.key + '-sal'"
                  class="cell-data cell-sal" :class="{ 'day-col': isDay(i) }">
                <template v-if="data[p.key] && pillarSinSals(i).length">
                  <div v-for="s in pillarSinSals(i)" :key="s.name" class="sal-item">
                    <span class="sal-sign" :style="sinSalSignColor(s.type)">{{ s.type === 'lucky' ? '＋' : s.type === 'unlucky' || s.type === 'warning' ? '－' : '･' }}</span><span style="color: var(--text-secondary);">{{ s.name }}</span>
                  </div>
                </template>
                <span v-else style="color: var(--border-subtle);">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 기둥 레이블 푸터 -->
    <div class="pillar-footer">
      <div class="col-label-spacer"></div>
      <div v-for="(p, i) in pillars" :key="p.key + '-footer'" class="pillar-label">
        <span :style="isDay(i) ? `color: ${ec('화')};` : 'color: var(--text-muted);'">
          {{ p.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── 래퍼 ── */
.saju-table-wrap {
  --fs-ganji:       2.8rem;
  --fs-ganji-hanja: 1.4rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ── 블록 카드 ── */
.table-block {
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
}

/* ── 테이블 기본 ── */
.saju-table {
  width: 100%;
  min-width: 340px;
  border-collapse: collapse;
  text-align: center;
  table-layout: fixed;
}

/* 열 너비 */
col.col-label { width: 3.2rem; }

/* ── 셀 공통 ── */
.cell-label {
  background: var(--surface-2);
  border-right: 1px solid var(--surface-3);
}
.row-label {
  font-size: var(--fs-label);
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.1em;
  padding: 8px 4px;
}
.cell-head {
  padding: 10px 6px;
  font-size: var(--fs-label);
  font-weight: 500;
}
.cell-data {
  padding: 6px 4px;
}
.day-col {
  background: color-mix(in srgb, var(--el-화) 3%, var(--surface-1));
}

/* ── 헤더 행 ── */
.header-row {
  border-bottom: 1px solid var(--border-subtle);
}
.header-row .cell-label {
  border-bottom: 1px solid var(--border-subtle);
}

/* ── 간지 셀 ── */
.cell-ganji {
  text-align: center;
  vertical-align: middle;
  padding: 14px 4px 8px;
}
.ganji-wrap {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
}
.ganji-pair {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
}
.ganji-main {
  font-family: var(--font-ganji);
  font-size: var(--fs-ganji);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.01em;
}
.ganji-hanja {
  font-family: var(--font-ganji);
  font-size: var(--fs-ganji-hanja);
  font-weight: 700;
  line-height: 1;
  opacity: 0.5;
  margin-bottom: 4px;
}
.el-sign {
  font-size: var(--fs-label);
  font-weight: 600;
  opacity: 0.75;
  margin-top: 2px;
}

/* ── 시주 미입력 대시 ── */
.null-dash {
  font-size: var(--fs-ganji-hanja);
  color: var(--text-muted);
  display: block;
  padding: 14px 0;
}

/* ── 작은 텍스트 셀 ── */
.cell-sm {
  font-size: var(--fs-label);
  padding: 8px 4px;
  border-top: 1px solid var(--surface-3);
}

/* ── 신살 셀 ── */
.cell-sal {
  padding: 10px 4px;
  border-top: 1px solid var(--surface-3);
}
.sal-item {
  font-size: var(--fs-label);
  font-weight: 500;
  line-height: 1.7;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1px;
}
.sal-sign {
  font-size: 10px;
  font-weight: 700;
  opacity: 0.85;
  flex-shrink: 0;
}

/* ── 푸터 ── */
.pillar-footer {
  display: flex;
  align-items: center;
  padding: 0;
}
.col-label-spacer {
  width: 3.2rem;
  flex-shrink: 0;
}
.pillar-label {
  flex: 1;
  text-align: center;
  font-size: var(--fs-label);
  font-weight: 500;
  letter-spacing: 0.1em;
}

/* ── 반응형: 태블릿 (640px 이하) ── */
@media (max-width: 640px) {
  .saju-table-wrap {
    --fs-ganji:       2.2rem;
    --fs-ganji-hanja: 1.1rem;
  }
  .saju-table { min-width: 300px; }
  col.col-label { width: 2.8rem; }
  .cell-ganji { padding: 10px 2px 20px; }
  .col-label-spacer { width: 2.8rem; }
}

/* ── 반응형: 모바일 (400px 이하) ── */
@media (max-width: 400px) {
  .saju-table-wrap {
    --fs-ganji:       1.8rem;
    --fs-ganji-hanja: 0.9rem;
  }
  .saju-table { min-width: 260px; }
  col.col-label { width: 2.4rem; }
  .col-label-spacer { width: 2.4rem; }
  .row-label { font-size: 10px; }
}
</style>
