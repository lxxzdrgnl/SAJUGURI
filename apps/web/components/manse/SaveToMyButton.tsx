'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { ApiClient, createProfile } from '@sajuguri/api-client'
import type { SajuCalcRequest } from '@sajuguri/api-client'
import Card from '@/components/ui/Card'
import Button, { buttonClass } from '@/components/ui/Button'

interface Props {
  birthInput: SajuCalcRequest
  isLoggedIn: boolean
  googleLoginUrl: string
}

export default function SaveToMyButton({ birthInput, isLoggedIn, googleLoginUrl }: Props) {
  const t = useTranslations('manse.result.shared')
  const [state, setState] = useState<'idle' | 'busy' | 'done' | 'error'>('idle')

  async function handleSave() {
    if (state === 'busy' || state === 'done') return
    setState('busy')
    try {
      const api = new ApiClient('')
      await createProfile(api, {
        name: birthInput.name ?? '',
        birth_date: birthInput.birth_date,
        birth_time: birthInput.birth_time,
        calendar: birthInput.calendar,
        gender: birthInput.gender,
        is_leap_month: birthInput.is_leap_month,
        city: birthInput.city,
        longitude: birthInput.birth_longitude,
      })
      setState('done')
    } catch {
      setState('error')
    }
  }

  if (!isLoggedIn) {
    return (
      <Card className="mt-2 flex flex-col gap-3 p-4">
        <p className="text-[13px] text-c-text-sub">{t('saveToMyLoginHint')}</p>
        <a href={googleLoginUrl} className={`${buttonClass('secondary', 'md')} w-full`}>
          {t('saveToMyLoginLink')}
        </a>
      </Card>
    )
  }

  return (
    <Button
      type="button"
      variant={state === 'done' ? 'primary' : 'secondary'}
      onClick={handleSave}
      disabled={state === 'busy' || state === 'done'}
      className={`mt-2 w-full disabled:opacity-60 ${state === 'error' ? 'text-c-danger' : ''}`}
    >
      {state === 'done'
        ? t('saveToMySuccess')
        : state === 'error'
          ? t('saveToMyError')
          : t('saveToMyTitle')}
    </Button>
  )
}
