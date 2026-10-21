'use client'

/**
 * 인라인 상대 만세력 선택/입력 카드 (B5).
 * `request_partner` SSE 이벤트 수신 시 대화 흐름 내에 표시.
 * 인라인 카드(프롬프트 + 버튼)는 그대로 두고, 버튼을 누르면 공용 MansePickerSheet를 연다.
 */
import { useState } from 'react'
import { useTranslations } from 'next-intl'
import type { ProfileResponse, PartnerAttachRequest } from '@sajuguri/api-client'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import MansePickerSheet, { type MansePick } from '@/components/manse/MansePickerSheet'

interface Props {
  profiles: ProfileResponse[]
  onSelect: (p: ProfileResponse) => void
  onSubmitBirth: (body: PartnerAttachRequest) => Promise<void>
}

export default function InlinePartnerCard({ profiles, onSelect, onSubmitBirth }: Props) {
  const t = useTranslations('chat')
  const [sheetOpen, setSheetOpen] = useState(false)

  async function handlePick(pick: MansePick) {
    if (pick.profile_id != null) {
      const profile = profiles.find((p) => p.id === pick.profile_id)
      if (profile) onSelect(profile)
      return
    }
    await onSubmitBirth({
      birth_date: pick.birth_date,
      gender: pick.gender,
      calendar: pick.calendar,
      is_leap_month: pick.is_leap_month,
      ...(pick.birth_time ? { birth_time: pick.birth_time } : {}),
      ...(pick.name?.trim() ? { name: pick.name.trim() } : {}),
    })
  }

  return (
    <>
      <Card tone="soft" className="w-full p-4">
        <p className="mb-3 text-[13px] font-extrabold text-c-text">{t('inlinePartner.prompt')}</p>
        <Button
          size="sm"
          onClick={() => setSheetOpen(true)}
        >
          {t('inlinePartner.action')}
        </Button>
      </Card>

      <MansePickerSheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        profiles={profiles}
        title={t('inlinePartner.sheetTitle')}
        onPick={handlePick}
      />
    </>
  )
}
