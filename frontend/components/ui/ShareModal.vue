<script setup lang="ts">
const props = defineProps<{ show: boolean; url: string }>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()

const copied = ref(false)

async function copy() {
  try {
    await navigator.clipboard.writeText(props.url)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {}
}

// 모달 열릴 때 자동 복사
watch(() => props.show, (val) => { if (val) copy() })

function close() { emit('update:show', false) }
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-backdrop" @click.self="close">
        <div class="modal-sheet modal-sheet--left">
          <div class="modal-header">
            <p class="modal-title">공유하기</p>
            <button class="modal-close" @click="close">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p class="modal-subdesc">아래 링크를 공유하세요</p>
          <div class="modal-link-box">
            <span class="modal-link-text">{{ url }}</span>
          </div>
          <button class="modal-copy-btn" @click="copy">
            <svg v-if="copied" viewBox="0 0 24 24" fill="none" class="icon">
              <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" class="icon">
              <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ copied ? '복사됨!' : '링크 복사' }}
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 1000;
}
@media (min-width: 480px) { .modal-backdrop { align-items: center; } }
.modal-sheet {
  width: 100%; max-width: 440px;
  background: var(--surface-1);
  border-radius: 20px 20px 0 0;
  padding: 24px 20px 32px;
  display: flex; flex-direction: column; gap: 14px;
}
@media (min-width: 480px) { .modal-sheet { border-radius: 24px; padding: 32px 28px; } }
.modal-sheet--left { text-align: left; }
.modal-header { display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 18px; font-weight: 800; color: var(--text-primary); }
.modal-subdesc { font-size: var(--fs-sub); color: var(--text-muted); }
.modal-close {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: none;
  border-radius: 8px; cursor: pointer; color: var(--text-muted); flex-shrink: 0;
}
.modal-close svg { width: 16px; height: 16px; }
.modal-close:hover { background: var(--surface-2); }
.modal-link-box {
  background: var(--surface-2); border: 1px solid var(--border-subtle);
  border-radius: 10px; padding: 12px 14px;
}
.modal-link-text { font-size: 13px; color: var(--text-secondary); word-break: break-all; display: block; }
.modal-copy-btn {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; width: 100%; padding: 13px; border-radius: 12px;
  border: none; background: var(--accent); color: #fff;
  font-size: var(--fs-body); font-weight: 700;
  cursor: pointer; transition: opacity 0.15s; margin-top: 4px;
}
.modal-copy-btn:hover { opacity: 0.88; }
.icon { width: 16px; height: 16px; flex-shrink: 0; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .modal-sheet, .modal-leave-active .modal-sheet { transition: transform 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-sheet, .modal-leave-to .modal-sheet { transform: translateY(40px); }
</style>
