import { useTranslations } from 'next-intl'
import InputForm from '@/components/manse/InputForm'

export default function NewManse() {
  const t = useTranslations('manse.form')
  return (
    <main className="-mx-4 -mb-8 -mt-2 min-h-[calc(100dvh-3.5rem)] px-4 pb-10 pt-4 text-c-text">
      <h1 className="mb-4 font-display text-2xl font-normal leading-tight">{t('title')}</h1>
      <InputForm />
    </main>
  )
}
