<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { STORAGE_KEYS } from '~/utils/storageKeys'

const route = useRoute()
const auth = useAuthStore()
const config = useRuntimeConfig()

onMounted(async () => {
  const accessToken = route.query.access_token as string | undefined
  const refreshToken = route.query.refresh_token as string | undefined

  if (!accessToken || !refreshToken) {
    navigateTo('/', { replace: true })
    return
  }

  auth.setTokens(accessToken, refreshToken)
  await auth.fetchMe()

  // 로그인 전 저장 시도했던 만세력 자동 저장
  const pending = localStorage.getItem(STORAGE_KEYS.SAJU_PENDING_SAVE)
  if (pending) {
    try {
      await $fetch(`${config.public.apiBase}/api/profiles`, {
        method: 'POST',
        body: JSON.parse(pending),
        headers: { Authorization: `Bearer ${accessToken}` },
      })
    } catch { /* 저장 실패해도 계속 진행 */ }
    localStorage.removeItem(STORAGE_KEYS.SAJU_PENDING_SAVE)
  }

  const redirect = localStorage.getItem(STORAGE_KEYS.SAJU_LOGIN_REDIRECT) || '/profile'
  localStorage.removeItem(STORAGE_KEYS.SAJU_LOGIN_REDIRECT)
  navigateTo(redirect, { replace: true })
})
</script>

<template>
  <div class="callback-wrap">
    <p class="callback-msg">로그인 처리 중...</p>
  </div>
</template>

<style scoped>
.callback-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-base);
}

.callback-msg {
  color: var(--text-muted);
  font-size: var(--fs-body);
}
</style>
