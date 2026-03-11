<script setup lang="ts">
import { computed } from 'vue'
import type { SinSal } from '~/types/saju'

const props = defineProps<{ sinSals: SinSal[] }>()

const lucky   = computed(() => props.sinSals.filter(s => s.type === 'lucky'))
const unlucky = computed(() => props.sinSals.filter(s => s.type === 'unlucky' || s.type === 'warning'))
const neutral = computed(() => props.sinSals.filter(s => s.type === 'neutral'))
</script>

<template>
  <div class="card space-y-3">
    <h3 class="label-section">신살 (神殺)</h3>
    <div class="sinsal-grid">
      <div class="sinsal-col">
        <div class="col-hd lucky-hd">길신 (吉神)</div>
        <div v-if="lucky.length" class="sinsal-list">
          <div v-for="s in lucky" :key="s.name" class="sinsal-row">
            <span class="dot" style="color: var(--el-목);">●</span>
            <span class="sname">{{ s.name }}</span>
            <span v-if="s.priority === 'high'" class="pbadge pbadge-lucky">강</span>
          </div>
        </div>
        <div v-else class="empty">없음</div>
      </div>

      <div class="sinsal-col">
        <div class="col-hd unlucky-hd">실성 (失星)</div>
        <div v-if="unlucky.length" class="sinsal-list">
          <div v-for="s in unlucky" :key="s.name" class="sinsal-row">
            <span class="dot" style="color: var(--el-화);">●</span>
            <span class="sname">{{ s.name }}</span>
            <span v-if="s.priority === 'high'" class="pbadge pbadge-unlucky">강</span>
          </div>
        </div>
        <div v-else class="empty">없음</div>
      </div>
    </div>

    <div v-if="neutral.length" class="neutral-row">
      <span style="font-size: var(--fs-label); color: #aaaaaa;">중립:</span>
      <span v-for="s in neutral" :key="s.name" class="neutral-chip">{{ s.name }}</span>
    </div>
  </div>
</template>

<style scoped>
.sinsal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.sinsal-col {
  background: #faf8f6;
  border: 1px solid #f0ece8;
  border-radius: 8px;
  overflow: hidden;
}
.col-hd {
  padding: 7px 12px;
  font-size: var(--fs-label);
  font-weight: 600;
  letter-spacing: 0.05em;
}
.lucky-hd {
  background: color-mix(in srgb, var(--el-목) 8%, transparent);
  color: var(--el-목);
  border-bottom: 1px solid color-mix(in srgb, var(--el-목) 18%, transparent);
}
.unlucky-hd {
  background: color-mix(in srgb, var(--el-화) 8%, transparent);
  color: var(--el-화);
  border-bottom: 1px solid color-mix(in srgb, var(--el-화) 18%, transparent);
}
.sinsal-list { padding: 4px 0; }
.sinsal-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  font-size: var(--fs-label);
  color: var(--text-primary);
}
.dot { font-size: 7px; flex-shrink: 0; }
.sname { flex: 1; }
.pbadge {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
}
.pbadge-lucky {
  background: color-mix(in srgb, var(--el-목) 12%, transparent);
  color: var(--el-목);
}
.pbadge-unlucky {
  background: color-mix(in srgb, var(--el-화) 12%, transparent);
  color: var(--el-화);
}
.empty {
  padding: 12px;
  font-size: var(--fs-label);
  color: #cccccc;
  text-align: center;
}
.neutral-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  padding-top: 4px;
  border-top: 1px solid #f0ece8;
}
.neutral-chip {
  font-size: var(--fs-label);
  color: #888888;
  padding: 2px 8px;
  background: #f0ece8;
  border-radius: 4px;
}
</style>
