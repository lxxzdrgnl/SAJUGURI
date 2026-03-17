import { useAuthStore } from '~/stores/auth'

export type SaveState = 'idle' | 'loading' | 'done' | 'exists' | 'error'

export interface ProfileSaveBody {
  name: string
  birth_date: string
  birth_time: string | null
  calendar: string
  gender: string
  is_leap_month: boolean
  city?: string | null
  longitude?: number | null
}

export function useProfileSave() {
  const auth = useAuthStore()
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  const saveState = ref<SaveState>('idle')

  async function saveProfile(body: ProfileSaveBody) {
    saveState.value = 'loading'
    try {
      await auth.authFetch(`${base}/api/profiles`, {
        method: 'POST',
        body,
      })
      saveState.value = 'done'
    } catch (e: unknown) {
      const status = (e as { response?: { status?: number } })?.response?.status
      saveState.value = status === 409 ? 'exists' : 'error'
      setTimeout(() => { saveState.value = 'idle' }, 2500)
    }
  }

  const saveLabel = computed(() => {
    switch (saveState.value) {
      case 'loading': return '저장 중…'
      case 'done':    return '저장 완료 ✓'
      case 'exists':  return '이미 저장된 만세력'
      case 'error':   return '저장 실패 — 다시 시도'
      default:        return '만세력 저장하기'
    }
  })

  const saveDisabled = computed(() =>
    saveState.value === 'loading' || saveState.value === 'done' || saveState.value === 'exists'
  )

  return { saveState, saveProfile, saveLabel, saveDisabled }
}
