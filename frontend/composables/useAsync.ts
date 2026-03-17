/**
 * 공통 loading / error 상태 + try/catch/finally 보일러플레이트 래퍼.
 *
 * @example
 * const { loading, error, run } = useAsync()
 * const data = await run(() => api.getList(), '불러오기 실패')
 * if (data) { ... }
 */
export function useAsync() {
  const loading = ref(false)
  const error   = ref('')

  /**
   * @param fn        실행할 비동기 함수
   * @param errorMsg  실패 시 error 에 표시할 문자열 (undefined 이면 error 를 건드리지 않음)
   * @returns         성공 시 fn 반환값, 실패 시 null
   */
  async function run<T>(fn: () => Promise<T>, errorMsg?: string): Promise<T | null> {
    loading.value = true
    error.value   = ''
    try {
      return await fn()
    } catch {
      if (errorMsg !== undefined) error.value = errorMsg
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
