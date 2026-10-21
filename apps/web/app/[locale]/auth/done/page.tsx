'use client'

import { useEffect } from 'react'
import { useTranslations } from 'next-intl'
import { consumeReturnTo } from '@/lib/loginReturn'
import ScreenShell from '@/components/ui/ScreenShell'

/**
 * OAuth 콜백 착지 페이지. 백엔드가 httpOnly 쿠키를 심고 여기로 리다이렉트한다.
 * 쿠키는 이미 브라우저에 저장됐으므로, 로그인 직전 화면(없으면 홈)으로 교체 이동만 한다.
 */
export default function AuthDone() {
  const t = useTranslations('auth')
  useEffect(() => {
    // 저장된 경로는 언어 프리픽스(/en)를 이미 포함하므로 locale 라우터 대신 전체 이동
    window.location.replace(consumeReturnTo() ?? '/')
  }, [])
  return (
    <ScreenShell center>
      <p className="text-sm font-extrabold text-c-text-sub">{t('signingIn')}</p>
    </ScreenShell>
  )
}
