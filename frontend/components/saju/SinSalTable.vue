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
            <span class="dot" style="color: var(--color-good);">●</span>
            <div class="sname-col">
              <span class="sname">{{ s.name }}</span>
              <span v-if="s.desc" class="sdesc">{{ s.desc }}</span>
            </div>
            <span v-if="s.priority === 'high'" class="pbadge pbadge-lucky">강</span>
          </div>
        </div>
        <div v-else class="empty">없음</div>
      </div>

      <div class="sinsal-col">
        <div class="col-hd unlucky-hd">실성 (失星)</div>
        <div v-if="unlucky.length" class="sinsal-list">
          <div v-for="s in unlucky" :key="s.name" class="sinsal-row">
            <span class="dot" style="color: var(--color-bad);">●</span>
            <div class="sname-col">
              <span class="sname">{{ s.name }}</span>
              <span v-if="s.desc" class="sdesc">{{ s.desc }}</span>
            </div>
            <span v-if="s.priority === 'high'" class="pbadge pbadge-unlucky">강</span>
          </div>
        </div>
        <div v-else class="empty">없음</div>
      </div>
    </div>

    <div v-if="neutral.length" class="neutral-wrap">
      <div v-for="s in neutral" :key="s.name" class="neutral-item">
        <span class="neutral-name">{{ s.name }}</span>
        <span v-if="s.desc" class="sdesc">{{ s.desc }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sinsal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
@media (max-width: 400px) {
  .sinsal-grid { grid-template-columns: 1fr; }
}
.sinsal-col {
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
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
  background: color-mix(in srgb, var(--color-good) 8%, transparent);
  color: var(--color-good);
  border-bottom: 1px solid color-mix(in srgb, var(--color-good) 18%, transparent);
}
.unlucky-hd {
  background: color-mix(in srgb, var(--color-bad) 8%, transparent);
  color: var(--color-bad);
  border-bottom: 1px solid color-mix(in srgb, var(--color-bad) 18%, transparent);
}
.sinsal-list { padding: 0; }
.sinsal-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 7px 12px;
  font-size: var(--fs-label);
  color: var(--text-primary);
  border-bottom: 1px solid var(--surface-3);
}
.sinsal-list .sinsal-row:last-child { border-bottom: none; }
.dot { font-size: 7px; flex-shrink: 0; margin-top: 3px; }
.sname-col { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.sname { font-size: var(--fs-label); color: var(--text-primary); }
.sdesc { font-size: 10px; color: var(--text-muted); line-height: 1.4; }
.pbadge {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
}
.pbadge-lucky {
  background: color-mix(in srgb, var(--color-good) 12%, transparent);
  color: var(--color-good);
}
.pbadge-unlucky {
  background: color-mix(in srgb, var(--color-bad) 12%, transparent);
  color: var(--color-bad);
}
.empty {
  padding: 12px;
  font-size: var(--fs-label);
  color: var(--text-muted);
  text-align: center;
}
.neutral-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 6px;
  border-top: 1px solid var(--border-subtle);
}
.neutral-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 5px 10px;
  background: var(--surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  min-width: 80px;
}
.neutral-name {
  font-size: var(--fs-label);
  color: var(--text-secondary);
  font-weight: 600;
}
</style>
