<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

defineProps<{ text: string }>()

const pinned  = ref(false)
const hovered = ref(false)
const visible = computed(() => pinned.value || hovered.value)
const wrapRef = ref<HTMLElement | null>(null)

const TIP_W = 220
const pos = ref({ top: 0, left: 0 })
const tailLeft = ref('50%')

function calcPos() {
  if (!wrapRef.value) return
  const rect = wrapRef.value.getBoundingClientRect()
  const vw   = window.innerWidth
  const btnCx = rect.left + rect.width / 2

  let left = btnCx - TIP_W / 2
  // 오른쪽 화면 밖
  if (left + TIP_W > vw - 8) left = vw - TIP_W - 8
  // 왼쪽 화면 밖
  if (left < 8) left = 8

  const tailX = Math.min(Math.max(btnCx - left, 16), TIP_W - 16)
  tailLeft.value = `${tailX}px`
  pos.value = { top: rect.top - 8, left }
}

function onMouseEnter() { calcPos(); hovered.value = true }
function onMouseLeave() { hovered.value = false }
function onClick(e: MouseEvent) {
  e.stopPropagation()
  calcPos()
  pinned.value = !pinned.value
}

function onOutside(e: MouseEvent) {
  if (wrapRef.value && !wrapRef.value.contains(e.target as Node)) {
    pinned.value  = false
    hovered.value = false
  }
}

onMounted(()   => document.addEventListener('click', onOutside))
onUnmounted(() => document.removeEventListener('click', onOutside))
</script>

<template>
  <span ref="wrapRef" class="tt-wrap">
    <button
      class="tt-btn"
      type="button"
      aria-label="설명 보기"
      @mouseenter="onMouseEnter"
      @mouseleave="onMouseLeave"
      @click="onClick"
    >?</button>

    <Teleport to="body">
      <Transition name="tt">
        <span
          v-if="visible"
          class="tt-box"
          role="tooltip"
          :style="`top: ${pos.top}px; left: ${pos.left}px; --tail-left: ${tailLeft};`"
          @click.stop
        >
          {{ text }}
        </span>
      </Transition>
    </Teleport>
  </span>
</template>

<style scoped>
.tt-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.tt-btn {
  width: var(--tt-size);
  height: var(--tt-size);
  border-radius: 50%;
  border: 1.5px solid var(--tt-color);
  background: transparent;
  color: var(--tt-color);
  font-size: var(--tt-font-size);
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}
.tt-btn:hover {
  background: var(--tt-hover-bg);
  border-color: var(--tt-hover-bg);
  color: #ffffff;
}
</style>

<style>
/* Teleport로 body에 렌더링되므로 scoped 불가 */
.tt-box {
  position: fixed;
  transform: translateY(-100%);
  width: 220px;
  background: var(--text-primary);
  color: #ffffff;
  font-size: 11px;
  line-height: 1.6;
  padding: 8px 10px;
  border-radius: 8px;
  pointer-events: none;
  z-index: 9999;
  white-space: normal;
  word-break: keep-all;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}

.tt-box::after {
  content: '';
  position: absolute;
  top: 100%;
  left: var(--tail-left, 50%);
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--text-primary);
}

.tt-enter-active, .tt-leave-active { transition: opacity 0.15s, transform 0.15s; }
.tt-enter-from, .tt-leave-to  { opacity: 0; transform: translateY(calc(-100% + 4px)); }
.tt-enter-to,   .tt-leave-from { opacity: 1; transform: translateY(-100%); }
</style>
