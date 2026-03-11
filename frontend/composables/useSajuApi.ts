import type { SajuCalcRequest, SajuCalcResponse, WolUnEntry, YeonUnEntry, IlJinEntry } from '~/types/saju'

export function useSajuApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  async function calcSaju(req: SajuCalcRequest): Promise<SajuCalcResponse> {
    const data = await $fetch<SajuCalcResponse>(`${base}/api/saju/calc`, {
      method: 'POST',
      body: req,
    })
    return data
  }

  async function getWolUn(year: number, dayStem: string): Promise<WolUnEntry[]> {
    return $fetch<WolUnEntry[]>(`${base}/api/saju/wol-un`, {
      query: { year, day_stem: dayStem },
    })
  }

  async function getYeonUn(startYear: number, count: number, dayStem: string): Promise<YeonUnEntry[]> {
    return $fetch<YeonUnEntry[]>(`${base}/api/saju/yeon-un`, {
      query: { start_year: startYear, count, day_stem: dayStem },
    })
  }

  async function getIlJin(year: number, month: number): Promise<IlJinEntry[]> {
    return $fetch<IlJinEntry[]>(`${base}/api/saju/il-jin`, {
      query: { year, month },
    })
  }

  return { calcSaju, getWolUn, getYeonUn, getIlJin }
}
