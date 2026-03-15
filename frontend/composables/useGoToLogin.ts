export function useGoToLogin() {
  const route = useRoute()

  return function goToLogin(redirectPath?: string) {
    if (import.meta.client) {
      localStorage.setItem('saju_login_redirect', redirectPath ?? route.fullPath)
    }
    navigateTo('/login')
  }
}
