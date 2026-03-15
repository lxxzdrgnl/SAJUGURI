<script setup lang="ts">
const props = defineProps<{ data: Record<string, number> }>()

const elements = ['목', '화', '토', '금', '수']

function ec(el: string) { return elColor(el) }

function judge(el: string) {
  const pct = props.data[el] ?? 0
  if (pct < 10) return { label: '부족', style: 'color: var(--el-수);' }
  if (pct > 30) return { label: '과다', style: 'color: var(--el-화);' }
  return { label: '적정', style: 'color: var(--el-목);' }
}

// 균형도 점수 = 100 - 편차 합계/2 (각 오행이 20%일 때 완벽한 균형)
const balanceScore = computed(() => {
  const total = Object.values(props.data).reduce((a, b) => a + b, 0)
  if (total === 0) return 0
  const dev = elements.reduce((sum, el) => sum + Math.abs((props.data[el] ?? 0) - 20), 0)
  return Math.max(0, Math.round(100 - dev / 2))
})

const overElements  = computed(() => elements.filter(el => (props.data[el] ?? 0) > 30))
const lackElements  = computed(() => elements.filter(el => (props.data[el] ?? 0) < 10))

const balanceSummary = computed(() => {
  const parts: string[] = []
  if (overElements.value.length)  parts.push(`${overElements.value.join('·')} 과다`)
  if (lackElements.value.length)  parts.push(`${lackElements.value.join('·')} 결핍`)
  if (parts.length === 0) return '균형 잡힌 오행 구성입니다'
  return parts.join(' + ')
})

const balanceLabel = computed(() => {
  const s = balanceScore.value
  if (s >= 80) return { text: '균형', color: 'var(--color-good)' }
  if (s >= 60) return { text: '보통', color: 'var(--el-토)' }
  return { text: '불균형', color: 'var(--color-bad)' }
})
</script>

<template>
  <div class="balance-wrap" style="border-top: 1px solid var(--border-subtle); border-radius: 0 0 12px 12px;">
    <!-- 균형도 요약 -->
    <div class="balance-summary">
      <span class="bs-label">오행 균형도</span>
      <span class="bs-score" :style="`color: ${balanceLabel.color};`">{{ balanceScore }} / 100</span>
      <span class="bs-tag" :style="`color: ${balanceLabel.color}; background: color-mix(in srgb, ${balanceLabel.color} 10%, transparent); border-color: color-mix(in srgb, ${balanceLabel.color} 25%, transparent);`">
        {{ balanceLabel.text }}
      </span>
      <span class="bs-desc" style="color: var(--text-muted);">{{ balanceSummary }}</span>
    </div>
    <table class="balance-table">
      <thead>
        <tr>
          <th class="th">오행</th>
          <th class="th th-num">비율</th>
          <th class="th">분포</th>
          <th class="th th-num">판정</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="el in elements" :key="el">
          <td class="td">
            <span class="el-label" :style="`color: ${ec(el)};`">{{ el }}</span>
          </td>
          <td class="td td-num" :style="`color: ${ec(el)}; font-weight: 600;`">
            {{ data[el] ?? 0 }}%
          </td>
          <td class="td td-bar">
            <div class="bar-bg">
              <div class="bar-fill" :style="`width: ${Math.min(data[el] ?? 0, 100)}%; background: ${ec(el)};`"/>
            </div>
          </td>
          <td class="td td-num">
            <span class="font-semibold" :style="judge(el).style">{{ judge(el).label }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.balance-wrap {
  background: var(--surface-1);
  border: none;
  overflow: hidden;
}
.balance-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 14px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--surface-3);
}
.bs-label {
  font-size: var(--fs-label);
  color: var(--text-muted);
  font-weight: 500;
}
.bs-score {
  font-size: var(--fs-body);
  font-weight: 700;
  min-width: 56px;
}
.bs-tag {
  font-size: var(--fs-tiny);
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
  border: 1px solid;
}
.bs-desc {
  font-size: var(--fs-tiny);
  flex: 1;
  min-width: 120px;
}
.balance-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-label);
}
.th {
  padding: 8px 12px;
  text-align: left;
  color: var(--text-muted);
  font-weight: 500;
  background: var(--surface-2);
  border-bottom: 1px solid var(--surface-3);
  letter-spacing: 0.05em;
}
.th-num { text-align: center; width: 3.5rem; }
.td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--surface-3);
}
.balance-table tr:last-child .td { border-bottom: none; }
.td-num { text-align: center; }
.td-bar { min-width: 80px; }
.bar-bg {
  height: 6px;
  background: var(--surface-3);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 3px;
  opacity: 0.65;
  transition: width 0.4s ease;
}

.el-label {
  font-size: 15px;
  font-weight: 700;
}
</style>
