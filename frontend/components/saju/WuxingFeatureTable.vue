<script setup lang="ts">
const props = defineProps<{
  dominant?: string[]   // 현재 사주의 과다 오행 (강조 표시용)
  weak?: string[]       // 부족 오행
}>()

const open = ref(false)

const FEATURES = [
  { el: '목', dir: '동 · 봄', traits: '창의·성장·인자함', body: '간·담·눈', jobs: '교육·의료·법' },
  { el: '화', dir: '남 · 여름', traits: '열정·표현·명랑함', body: '심장·소장·혀', jobs: '방송·영업·IT' },
  { el: '토', dir: '중앙 · 환절기', traits: '신뢰·중용·포용력', body: '위·비장·입', jobs: '부동산·금융·중개' },
  { el: '금', dir: '서 · 가을', traits: '의리·결단·정의감', body: '폐·대장·코', jobs: '군경·기계·법조' },
  { el: '수', dir: '북 · 겨울', traits: '지혜·유연·통찰력', body: '신장·방광·귀', jobs: '철학·유통·무역' },
]
</script>

<template>
  <div class="wf-wrap">
    <button class="wf-toggle" @click="open = !open">
      <span class="fs-label font-semibold" style="color: var(--text-secondary);">오행 특성 참고표</span>
      <svg
        class="wf-chevron"
        :class="{ 'wf-chevron--open': open }"
        viewBox="0 0 16 16" fill="none"
      >
        <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <div v-if="open" class="wf-table-wrap">
      <table class="wf-table">
        <thead>
          <tr>
            <th>오행</th>
            <th>방위·계절</th>
            <th>성격 특성</th>
            <th>관련 신체</th>
            <th>어울리는 직업</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="f in FEATURES"
            :key="f.el"
            :class="{
              'wf-dominant': dominant?.includes(f.el),
              'wf-weak': weak?.includes(f.el),
            }"
          >
            <td>
              <div class="wf-el-cell">
                <span class="wf-el-name" :style="`color: var(--el-${f.el});`">{{ f.el }}</span>
                <span v-if="dominant?.includes(f.el)" class="wf-tag wf-tag-over">과다</span>
                <span v-else-if="weak?.includes(f.el)" class="wf-tag wf-tag-lack">부족</span>
              </div>
            </td>
            <td>{{ f.dir }}</td>
            <td>{{ f.traits }}</td>
            <td>{{ f.body }}</td>
            <td>{{ f.jobs }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.wf-wrap {
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  overflow: hidden;
  background: var(--surface-1);
}
.wf-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
  color: inherit;
}
.wf-toggle:hover { background: var(--surface-2); }
.wf-chevron {
  width: 16px; height: 16px;
  color: var(--text-muted);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.wf-chevron--open { transform: rotate(180deg); }

.wf-table-wrap {
  overflow-x: auto;
  border-top: 1px solid var(--border-subtle);
}
.wf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-tiny);
  color: var(--text-secondary);
}
.wf-table thead th {
  padding: 7px 10px;
  text-align: left;
  font-weight: 600;
  background: var(--surface-2);
  color: var(--text-muted);
  border-bottom: 1px solid var(--surface-3);
  white-space: nowrap;
  font-size: var(--fs-tiny);
}
.wf-table tbody td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--surface-3);
  vertical-align: middle;
  line-height: 1.5;
}
.wf-table tbody tr:last-child td { border-bottom: none; }
.wf-dominant { background: color-mix(in srgb, var(--color-bad) 4%, transparent); }
.wf-weak     { background: color-mix(in srgb, var(--color-good) 4%, transparent); }

.wf-el-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}
.wf-el-name {
  font-size: var(--fs-sub);
  font-weight: 700;
}
.wf-tag {
  display: inline-block;
  font-size: var(--fs-tiny);
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: 600;
}
.wf-tag-over {
  background: color-mix(in srgb, var(--color-bad) 12%, transparent);
  color: var(--color-bad);
}
.wf-tag-lack {
  background: color-mix(in srgb, var(--color-good) 12%, transparent);
  color: var(--color-good);
}
</style>
