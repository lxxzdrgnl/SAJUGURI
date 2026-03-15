<script setup lang="ts">
withDefaults(defineProps<{
  show: boolean
  title: string
  desc?: string
  cancelText?: string
}>(), {
  desc: '',
  cancelText: '',
})

const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const close = () => emit('update:show', false)
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="dialog-backdrop" @click.self="close">
      <div class="dialog-box">
        <p class="dialog-title">{{ title }}</p>
        <p v-if="desc" class="dialog-desc">{{ desc }}</p>
        <div class="dialog-body">
          <slot />
        </div>
        <button v-if="cancelText" class="dialog-cancel" @click="close">{{ cancelText }}</button>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 20px;
}
.dialog-box {
  background: var(--surface-1);
  border: 1px solid var(--border-default);
  border-radius: 18px;
  padding: 28px 24px 20px;
  max-width: 340px; width: 100%;
  display: flex; flex-direction: column; gap: 10px;
}
.dialog-title {
  font-size: var(--fs-section);
  font-weight: 800;
  color: var(--text-primary);
}
.dialog-desc {
  font-size: var(--fs-sub);
  color: var(--text-muted);
  line-height: 1.6;
}
.dialog-body {
  display: flex; flex-direction: column; gap: 8px;
  margin-top: 4px;
}
.dialog-cancel {
  width: 100%; padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--border-default);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-body);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.dialog-cancel:hover { background: var(--surface-2); }
</style>
