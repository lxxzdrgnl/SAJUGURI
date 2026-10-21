import { useTranslations } from 'next-intl'
import InputForm from '@/components/manse/InputForm'
import ScreenShell from '@/components/ui/ScreenShell'

export default function NewManse() {
  const t = useTranslations('manse.form')
  return (
    <ScreenShell className="pb-2 pt-2 text-c-text">
      <h1 className="mb-4 font-display text-2xl font-normal leading-tight">{t('title')}</h1>
      <InputForm />
    </ScreenShell>
  )
}
