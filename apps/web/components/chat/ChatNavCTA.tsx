'use client'

/**
 * 챗 인라인 네비게이션 CTA.
 * 특정 툴 결과 직후 렌더되며, 클릭 시 기존 기능 페이지(href)로 이동한다.
 * (사주 풀 리포트 / 운세 등)
 */
import { useRouter } from 'next/navigation'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'

interface Props {
  title: string
  buttonLabel: string
  href: string
}

export default function ChatNavCTA({ title, buttonLabel, href }: Props) {
  const router = useRouter()

  return (
    <Card tone="soft" className="p-4">
      <p className="mb-3 text-[13px] font-extrabold leading-snug text-c-text">
        {title}
      </p>
      <Button
        className="w-full"
        onClick={() => router.push(href)}
      >
        {buttonLabel}
      </Button>
    </Card>
  )
}
