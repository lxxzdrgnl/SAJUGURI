/**
 * 로그인 페이지로 이동 시 현재 상태를 localStorage에 저장하고,
 * 로그인 후 돌아왔을 때 자동 복원하는 공통 로직
 */
export function useLoginStatePersist<T>(
  key: string,
  getState: () => T | null,
  onRestore: (state: T) => void,
) {
  onMounted(() => {
    if (!import.meta.client) return
    const saved = localStorage.getItem(key)
    if (!saved) return
    localStorage.removeItem(key)
    try { onRestore(JSON.parse(saved)) } catch { /* ignore */ }
  })

  onBeforeRouteLeave((to) => {
    if (to.path !== '/login') return
    const state = getState()
    if (state !== null) localStorage.setItem(key, JSON.stringify(state))
  })
}
