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
</script>

<template>
  <div class="balance-wrap">
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
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  overflow: hidden;
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
