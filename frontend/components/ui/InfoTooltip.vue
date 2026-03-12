<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

defineProps<{ text: string }>()

const pinned  = ref(false)   // 클릭/터치로 고정
const hovered = ref(false)   // 호버로 임시 표시
const visible = computed(() => pinned.value || hovered.value)
const wrapRef = ref<HTMLElement | null>(null)

function onMouseEnter() { hovered.value = true }
function onMouseLeave() { hovered.value = false }
function onClick(e: MouseEvent) {
  e.stopPropagation()
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

    <Transition name="tt">
      <span v-if="visible" class="tt-box" role="tooltip" @click.stop>
        {{ text }}
      </span>
    </Transition>
  </span>
</template>

<style scoped>
.tt-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.tt-btn {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid var(--text-muted);
  background: transparent;
  color: var(--text-muted);
  font-size: 10px;
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
  background: var(--text-primary);
  border-color: var(--text-primary);
  color: #ffffff;
}

/* 툴팁 박스 */
.tt-box {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 8px);
  transform: translateX(-50%);
  width: 220px;
  background: var(--text-primary);
  color: #ffffff;
  font-size: 11px;
  line-height: 1.6;
  padding: 8px 10px;
  border-radius: 8px;
  pointer-events: none;
  z-index: 100;
  white-space: normal;
  word-break: keep-all;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
}

/* 말풍선 꼬리 */
.tt-box::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--text-primary);
}

/* 화면 가장자리 잘림 방지: 오른쪽 정렬 옵션 */
@media (max-width: 400px) {
  .tt-box {
    left: auto;
    right: 0;
    transform: none;
    width: 190px;
  }
  .tt-box::after {
    left: auto;
    right: 8px;
    transform: none;
  }
}

/* 트랜지션 */
.tt-enter-active, .tt-leave-active { transition: opacity 0.15s, transform 0.15s; }
.tt-enter-from, .tt-leave-to       { opacity: 0; transform: translateX(-50%) translateY(4px); }
.tt-enter-to, .tt-leave-from       { opacity: 1; transform: translateX(-50%) translateY(0); }

@media (max-width: 400px) {
  .tt-enter-from, .tt-leave-to  { transform: translateY(4px); }
  .tt-enter-to, .tt-leave-from  { transform: translateY(0); }
}
</style>
