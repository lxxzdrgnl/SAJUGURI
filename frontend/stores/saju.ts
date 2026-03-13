import { defineStore } from 'pinia'
import type { SajuCalcRequest, SajuCalcResponse } from '~/types/saju'

export const useSajuStore = defineStore('saju', () => {
  const result = ref<SajuCalcResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastRequest = ref<SajuCalcRequest | null>(null)

  const { calcSaju } = useSajuApi()

  async function calculate(req: SajuCalcRequest) {
    loading.value = true
    error.value = null
    lastRequest.value = req
    try {
      result.value = await calcSaju(req)
    } catch (e: unknown) {
      const err = e as { data?: { message?: string }; message?: string }
      error.value = err.data?.message ?? err.message ?? '계산 중 오류가 발생했습니다.'
    } finally {
      loading.value = false
    }
  }

  function reset() {
    result.value = null
    error.value = null
    lastRequest.value = null
  }

  function restore(req: SajuCalcRequest, res: SajuCalcResponse) {
    lastRequest.value = req
    result.value = res
  }

  return { result, loading, error, lastRequest, calculate, reset, restore }
})
