<script setup lang="ts">
import type { DailyFortuneResponse } from '~/types/saju'

defineProps<{ result: DailyFortuneResponse }>()

const STEM_HANJA: Record<string,string> = {
  '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊',
  '기':'己','경':'庚','신':'辛','임':'壬','계':'癸',
}
const BRANCH_HANJA: Record<string,string> = {
  '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳',
  '오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥',
}
const STEM_EL: Record<string,string> = {
  '갑':'목','을':'목','병':'화','정':'화','무':'토',
  '기':'토','경':'금','신':'금','임':'수','계':'수',
}
const BRANCH_EL: Record<string,string> = {
  '자':'수','축':'토','인':'목','묘':'목','진':'토','사':'화',
  '오':'화','미':'토','신':'금','유':'금','술':'토','해':'수',
}
const EL_SWATCH: Record<string,string> = {
  '목':'var(--el-목)', '화':'var(--el-화)', '토':'var(--el-토)',
  '금':'var(--el-금)', '수':'var(--el-수)',
}
const CAT_ORDER = ['exam','money','love','career','health','social']

function elColor(el: string) {
  if (!el) return 'var(--text-secondary)'
  if (el === '수') return '#888'
  return `var(--el-${el})`
}

function scoreColor(score: number) {
  if (score >= 80) return 'var(--color-good)'
  if (score >= 60) return 'var(--accent)'
  if (score >= 45) return '#c07818'
  return 'var(--color-bad)'
}
</script>

<template>
  <!-- 요약 카드 -->
  <div class="card summary-card">
    <div class="summary-top">
      <div class="summary-ganji">
        <span class="ganji ganji-char" :style="`color: ${elColor(STEM_EL[result.day_ganji.stem] ?? '')}`">
          {{ STEM_HANJA[result.day_ganji.stem] }}
        </span>
        <span class="ganji ganji-char" :style="`color: ${elColor(BRANCH_EL[result.day_ganji.branch] ?? '')}`">
          {{ BRANCH_HANJA[result.day_ganji.branch] }}
        </span>
      </div>
      <p class="overall-text fs-body">{{ result.overall }}</p>
    </div>
    <div class="basis-row">
      <span class="basis-label fs-tiny">오늘의 근거</span>
      <span class="basis-text fs-tiny">{{ result.basis }}</span>
    </div>
  </div>

  <!-- 옷 색깔 + 오늘의 경계 -->
  <div class="info-row">
    <div class="card info-card">
      <div class="info-icon-row">
        <div v-if="result.clothing_color.element" class="el-swatch"
          :style="`background: ${EL_SWATCH[result.clothing_color.element] ?? 'var(--surface-3)'}`" />
        <span class="fs-label" style="font-weight:700;color:var(--text-primary);">오늘의 옷 색깔</span>
      </div>
      <p class="info-value fs-body">{{ result.clothing_color.color }}</p>
      <p class="info-reason fs-tiny">{{ result.clothing_color.reason }}</p>
    </div>
    <div class="card info-card caution-card">
      <div class="info-icon-row">
        <span class="caution-icon">⚠️</span>
        <span class="fs-label" style="font-weight:700;color:var(--color-bad);">오늘의 경계</span>
      </div>
      <p class="info-value fs-sub caution-text">{{ result.caution }}</p>
    </div>
  </div>

  <!-- 카테고리별 운세 -->
  <div class="fortunes-list">
    <div v-for="key in CAT_ORDER" :key="key" class="card fortune-card">
      <div class="fortune-top">
        <span class="fortune-label fs-body">{{ result.fortunes[key].label }}</span>
        <div class="fortune-score-col">
          <span class="score-num" :style="`color: ${scoreColor(result.fortunes[key].score)}`">
            {{ result.fortunes[key].score }}
          </span>
          <span class="fs-tiny" style="color:var(--text-muted);">/100</span>
        </div>
      </div>
      <div class="score-bar-row">
        <div class="score-bar-track">
          <div class="score-bar-fill"
            :style="`width:${result.fortunes[key].score}%; background:${scoreColor(result.fortunes[key].score)}`" />
        </div>
        <span class="level-badge fs-tiny" :style="`color:${scoreColor(result.fortunes[key].score)}`">
          {{ result.fortunes[key].level }}
        </span>
      </div>
      <p class="fortune-text fs-sub">{{ result.fortunes[key].text }}</p>
    </div>
  </div>

  <!-- 하단 액션 (슬롯) -->
  <slot name="actions" />
</template>

<style scoped>
.summary-card { display: flex; flex-direction: column; gap: 12px; }
.summary-top { display: flex; align-items: center; gap: 16px; }
.summary-ganji { display: flex; gap: 0; flex-shrink: 0; line-height: 1; }
.ganji-char { font-size: 52px; font-weight: 700; font-family: var(--font-ganji); letter-spacing: -0.02em; }
.overall-text { flex: 1; min-width: 0; color: var(--text-primary); font-weight: 500; line-height: 1.65; }

.basis-row {
  display: flex; flex-direction: column; gap: 6px;
  padding: 10px 12px; border-radius: 10px;
  background: var(--surface-2); border: 1px solid var(--border-subtle);
}
.basis-label { font-weight: 700; color: var(--el-토); white-space: nowrap; }
.basis-text { color: var(--text-secondary); line-height: 1.8; white-space: pre-line; }

.info-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.info-card { display: flex; flex-direction: column; gap: 6px; padding: 14px 16px; }
.info-icon-row { display: flex; align-items: center; gap: 6px; }
.el-swatch { width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
.caution-icon { font-size: 14px; }
.info-value { font-weight: 600; color: var(--text-primary); line-height: 1.4; }
.info-reason { color: var(--text-muted); line-height: 1.5; }
.caution-card .caution-text { color: var(--text-secondary); font-weight: 400; font-size: var(--fs-tiny); line-height: 1.55; }

.fortunes-list { display: flex; flex-direction: column; gap: 10px; }
.fortune-card { display: flex; flex-direction: column; gap: 8px; }
.fortune-top { display: flex; align-items: center; justify-content: space-between; }
.fortune-label { font-weight: 700; color: var(--text-primary); font-size: 17px; }
.fortune-score-col { display: flex; align-items: baseline; gap: 2px; flex-shrink: 0; }
.score-num { font-size: 26px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }
.score-bar-row { display: flex; align-items: center; gap: 8px; }
.score-bar-track { flex: 1; height: 4px; border-radius: 2px; background: var(--border-subtle); overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }
.level-badge { font-weight: 600; white-space: nowrap; }
.fortune-text { color: var(--text-secondary); line-height: 1.7; }

@media (min-width: 768px) {
  .ganji-char { font-size: 64px; }
  .fortunes-list { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
}
</style>
