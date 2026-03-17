<template>
  <svg :class="['animate-spin', sizeClass]" viewBox="0 0 40 40" fill="none">
    <circle cx="20" cy="20" r="17" stroke="var(--border-subtle)" stroke-width="3"/>
    <path d="M20 3a17 17 0 0 1 17 17" stroke="var(--accent)" stroke-width="3" stroke-linecap="round"/>
  </svg>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })
const sizeClass = computed(() => ({ sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }[props.size]))
</script>
