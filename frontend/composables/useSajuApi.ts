import type { SajuCalcRequest, SajuCalcResponse, WolUnEntry, YeonUnEntry, IlJinEntry, DailyFortuneRequest, DailyFortuneResponse, QuestionRequest, ConsultationResponse, ConsultationDetail, ConsultationHistoryItem, ProfileResponse } from '~/types/saju'

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

  async function getDailyFortune(req: DailyFortuneRequest): Promise<DailyFortuneResponse> {
    const d = new Date()
    const localDate = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return $fetch<DailyFortuneResponse>(`${base}/api/saju/daily`, {
      method: 'POST',
      body: { ...req, target_date: req.target_date ?? localDate },
    })
  }

  async function createDailyShare(birthInput: Record<string, unknown>): Promise<{ share_token: string; share_url: string }> {
    return $fetch(`${base}/api/share/daily`, {
      method: 'POST',
      body: { birth_input: birthInput },
    })
  }

  async function getDailyShareInput(token: string): Promise<{ birth_input: Record<string, unknown> }> {
    return $fetch(`${base}/api/share/daily/${token}`)
  }

  async function askQuestion(req: QuestionRequest, authToken?: string | null): Promise<ConsultationResponse> {
    return $fetch<ConsultationResponse>(`${base}/api/question`, {
      method: 'POST',
      body: req,
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : undefined,
    })
  }

  async function listConsultations(token: string): Promise<ConsultationHistoryItem[]> {
    return $fetch<ConsultationHistoryItem[]>(`${base}/api/question/history`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  async function createConsultationShare(id: number, token?: string | null): Promise<{ share_token: string }> {
    return $fetch<{ share_token: string }>(`${base}/api/question/${id}/share`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
  }

  async function getSharedConsultation(shareToken: string): Promise<ConsultationDetail> {
    return $fetch<ConsultationDetail>(`${base}/api/question/share/${shareToken}`)
  }

  async function deleteConsultation(id: number, token: string): Promise<void> {
    await $fetch(`${base}/api/question/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  // ── 프로필 API ──────────────────────────────────────────────────────────────

  async function getProfiles(token: string): Promise<ProfileResponse[]> {
    return $fetch<ProfileResponse[]>(`${base}/api/profiles`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  async function getRepresentativeProfile(token: string): Promise<ProfileResponse> {
    return $fetch<ProfileResponse>(`${base}/api/profiles/representative`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  }

  return { calcSaju, getWolUn, getYeonUn, getIlJin, getDailyFortune, createDailyShare, getDailyShareInput, askQuestion, listConsultations, createConsultationShare, getSharedConsultation, deleteConsultation, getProfiles, getRepresentativeProfile }
}
