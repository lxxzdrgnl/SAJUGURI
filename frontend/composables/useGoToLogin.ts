import { STORAGE_KEYS } from '~/utils/storageKeys'

export function useGoToLogin() {
  const route = useRoute()

  return function goToLogin(redirectPath?: string) {
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEYS.SAJU_LOGIN_REDIRECT, redirectPath ?? route.fullPath)
    }
    navigateTo('/login')
  }
}
