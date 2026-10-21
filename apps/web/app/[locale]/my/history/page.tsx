import { getTranslations } from 'next-intl/server'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import Card from '@/components/ui/Card'
import { buttonClass } from '@/components/ui/Button'
import MascotTinted from '@/components/ui/MascotTinted'
import HistoryFeedClient from '@/components/my/HistoryFeedClient'
import { fetchAllRecords } from '@/lib/records/registry'
import GoogleLoginLink from '@/components/auth/GoogleLoginLink'

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
      <main className="-mx-4 -mt-2 -mb-8 px-4 pb-8 pt-4 flex flex-col gap-4">
        <h1 className="font-display text-xl font-normal text-c-text">{t('history.title')}</h1>
        <Card className="flex flex-col items-center gap-4 py-8 text-center">
          <MascotTinted width={72} height={72} />
          <p className="text-[15px] font-extrabold">{t('history.loginRequired')}</p>
          <GoogleLoginLink
            
            className={`${buttonClass('primary', 'md')} w-full`}
          >
            {t('history.loginWithGoogle')}
          </GoogleLoginLink>
        </Card>
      </main>
    )
  }

  const authApi = await serverAuthApi()
  const records = await fetchAllRecords(authApi)

  return (
    <main className="-mx-4 -mt-2 -mb-8 px-4 pb-8 pt-4 flex flex-col gap-4">
      <h1 className="font-display text-xl font-normal text-c-text">{t('history.title')}</h1>

      <HistoryFeedClient records={records} initialType={type} />
    </main>
  )
}
