import { getTranslations } from 'next-intl/server'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import MascotTinted from '@/components/ui/MascotTinted'
import HistoryFeedClient from '@/components/my/HistoryFeedClient'
import { fetchAllRecords } from '@/lib/records/registry'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const GOOGLE_LOGIN_URL = `${API_URL}/api/auth/google?client=web`

export default async function HistoryPage({
  searchParams,
}: {
  searchParams: Promise<{ type?: string }>
}) {
  const t = await getTranslations('my')
  const user = await currentUser()
  const { type } = await searchParams

  if (!user) {
    return (
      <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex flex-col gap-4">
        <h1 className="font-display text-xl font-normal text-c-text">{t('history.title')}</h1>
        <Card className="flex flex-col items-center gap-4 py-8 text-center">
          <MascotTinted width={72} height={72} />
          <p className="text-[15px] font-extrabold">{t('history.loginRequired')}</p>
          <a
            href={GOOGLE_LOGIN_URL}
            className={`${buttonClass('primary', 'md')} w-full`}
          >
            {t('history.loginWithGoogle')}
          </a>
        </Card>
      </main>
    )
  }

  const authApi = await serverAuthApi()
  const records = await fetchAllRecords(authApi)

  return (
    <main className="-mx-4 -mt-2 -mb-8 bg-c-bg px-4 pb-8 pt-4 shadow-[0_0_0_100vmax_var(--c-bg)] [clip-path:inset(0_-100vmax_-100vmax)] flex flex-col gap-4">
      <h1 className="font-display text-xl font-normal text-c-text">{t('history.title')}</h1>

      <HistoryFeedClient records={records} initialType={type} />
    </main>
  )
}
