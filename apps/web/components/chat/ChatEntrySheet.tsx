'use client'

/**
 * 채팅 진입 시트 — 공용 MansePickerSheet로 만세력 선택 → 세션 생성 → /chat/[id] 이동.
 */
import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslations, useLocale } from 'next-intl'
import type { ProfileResponse, ChatSessionCreate } from '@sajuguri/api-client'
import { createSession } from '@sajuguri/api-client'
import { api } from '@/lib/api'
import MansePickerSheet, { type MansePick } from '@/components/manse/MansePickerSheet'

interface Props {
  open: boolean
  onClose: () => void
  profiles: ProfileResponse[]
  /** 새 세션 첫 입력창에 채워 둘 문구 — /chat/[id]?q= 로 넘긴다 */
  prefill?: string | null
}

export default function ChatEntrySheet({ open, onClose, profiles, prefill = null }: Props) {
  const t = useTranslations('chat')
  const locale = useLocale()
  const router = useRouter()
  const [creating, setCreating] = useState(false)

  const startSession = useCallback(
    async (body: ChatSessionCreate) => {
      if (creating) return
      setCreating(true)
      try {
        const session = await createSession(api, body)
        onClose()
        const qs = prefill ? `?q=${encodeURIComponent(prefill)}` : ''
        router.push(`/chat/${session.id}${qs}`)
      } catch {
        setCreating(false)
      }
    },
    [creating, onClose, router, prefill],
  )

  const handlePick = useCallback(
    (pick: MansePick) => {
      if (creating) return
      if (pick.profile_id != null) {
        startSession({ profile_id: pick.profile_id, language: locale })
      } else {
        startSession({
          birth_date: pick.birth_date,
          birth_time: pick.birth_time,
          gender: pick.gender,
          calendar: pick.calendar,
          is_leap_month: pick.is_leap_month,
          language: locale,
        })
      }
    },
    [creating, locale, startSession],
  )

  return (
    <MansePickerSheet
      open={open}
      onClose={onClose}
      profiles={profiles}
      title={t('pickSheet.title')}
      onPick={handlePick}
    />
  )
}
