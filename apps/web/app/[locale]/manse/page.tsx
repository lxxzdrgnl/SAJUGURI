import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/navigation'
import RecentList from '@/components/manse/RecentList'
import SavedList from '@/components/manse/SavedList'
import { buttonClass } from '@/components/ui/Button'
import { currentUser, serverAuthApi } from '@/lib/serverAuth'
import { listProfiles, type ProfileResponse } from '@sajuguri/api-client'

// 브라우저가 직접 여는 풀 URL — next.config rewrites를 타지 않도록 백엔드 절대 주소 사용.

export default async function ManseIndex() {
  const t = await getTranslations('manse.index')
  const ts = await getTranslations('manse.saved')
  const user = await currentUser()

  let profiles: ProfileResponse[] = []
  if (user) {
    try {
      profiles = await listProfiles(await serverAuthApi())
    } catch {
      profiles = []
    }
  }

  return (
    <main className="-mx-4 -mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)] px-4 pb-10 pt-4 text-c-text">
      <h1 className="mb-4 font-display text-2xl font-normal leading-tight">{t('title')}</h1>
      <Link href="/manse/new" className={`${buttonClass('primary', 'md')} mb-6 w-full`}>
        {t('new')}
      </Link>

      {user && (
        <section className="mb-6">
          <h2 className="mb-3 text-sm font-extrabold text-c-text-sub">{ts('title')}</h2>
          <SavedList profiles={profiles} />
        </section>
      )}

      <RecentList
        isLoggedIn={!!user}
        savedKeys={profiles.map((p) => `${p.birth_date}|${p.birth_time ?? ''}|${p.gender}`)}
      />
    </main>
  )
}
