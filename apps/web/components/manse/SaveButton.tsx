'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { createProfile, type ProfileCreateRequest } from '@sajuguri/api-client'
import { api } from '@/lib/api'
import Button from '@/components/ui/Button'

/** 분석 화면 하단 저장 버튼 — 로그인 상태에서만 렌더. 성공 시 "저장됨"으로 전환. */
export default function SaveButton({ input }: { input: ProfileCreateRequest }) {
  const t = useTranslations('manse.saved')
  const [state, setState] = useState<'idle' | 'busy' | 'done' | 'error'>('idle')

  async function onClick() {
    if (state === 'busy' || state === 'done') return
    setState('busy')
    try {
      await createProfile(api, input)
      setState('done')
    } catch {
      setState('error')
    }
  }

  const label =
    state === 'done' ? t('saved') : state === 'error' ? t('saveError') : t('save')

  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={state === 'busy' || state === 'done'}
      className="mt-1 w-full disabled:opacity-60"
    >
      {label}
    </Button>
  )
}
