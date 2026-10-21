'use client'

import { useEffect, useState } from 'react'
import { useLocale, useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'
import { ApiClient, deleteSession } from '@sajuguri/api-client'
import type { ChatSession, ProfileResponse } from '@sajuguri/api-client'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import ChatEntrySheet from './ChatEntrySheet'
import PageHeading from '@/components/ui/PageHeading'

interface Props {
  sessions: ChatSession[]
  profiles: ProfileResponse[]
  /** 새 상담 첫 입력 힌트 (?topic= / ?q=) — 있으면 새 상담 시트를 바로 연다 */
  prefill?: string | null
}

const SESSION_COLORS = ['bg-c-poster-butter', 'bg-c-poster-rose', 'bg-c-poster-lilac', 'bg-c-poster-peach', 'bg-c-poster-sky', 'bg-c-poster-mint']

function sessionColor(id: string): string {
  let hash = 0
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) >>> 0
  }
  return SESSION_COLORS[hash % SESSION_COLORS.length]
}

function formatDate(dt: string, locale: string) {
  return new Intl.DateTimeFormat(locale, { month: 'short', day: 'numeric' }).format(new Date(dt))
}

interface DeleteModalProps {
  sessionTitle: string
  onConfirm: () => void
  onClose: () => void
  t: ReturnType<typeof useTranslations>
}

function DeleteModal({ sessionTitle, onConfirm, onClose, t }: DeleteModalProps) {
  useEffect(() => {
    const original = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => {
      document.body.style.overflow = original
      document.removeEventListener('keydown', handleKey)
    }
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-c-scrim sm:items-center"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="w-full max-w-[480px] rounded-t-card bg-c-surface p-6 sm:rounded-card">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-[15px] font-extrabold text-c-text">{t('deleteConfirm')}</h2>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full border border-c-line text-c-text-sub"
            aria-label={t('deleteConfirmCancel')}
          >
            <svg viewBox="0 0 16 16" fill="none" className="h-4 w-4">
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <p className="mb-6 truncate rounded-card bg-c-surface-soft px-4 py-3 text-[14px] font-bold text-c-text">
          {sessionTitle}
        </p>

        <div className="flex gap-3">
          <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
            {t('deleteConfirmCancel')}
          </Button>
          <Button type="button" onClick={onConfirm} className="flex-1">
            {t('deleteConfirmYes')}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function ChatListClient({ sessions: initialSessions, profiles, prefill = null }: Props) {
  const t = useTranslations('chat')
  const locale = useLocale()
  const [sheetOpen, setSheetOpen] = useState(!!prefill)
  // 첫 입력 힌트는 한 번만 쓴다 — 시트를 닫으면 비워서 이후 "새 상담"에 남지 않게 한다
  const [activePrefill, setActivePrefill] = useState(prefill)

  // ?topic= / ?q= 를 읽었으면 주소에서 지운다 — 새로고침 때 시트가 다시 열리지 않게
  useEffect(() => {
    if (!prefill) return
    window.history.replaceState(window.history.state, '', window.location.pathname)
  }, [prefill])
  const [sessions, setSessions] = useState(initialSessions)
  const [deletingSession, setDeletingSession] = useState<ChatSession | null>(null)
  const [editMode, setEditMode] = useState(false)

  async function handleDelete(id: string) {
    setSessions((prev) => prev.filter((s) => s.id !== id))
    setDeletingSession(null)
    try {
      const api = new ApiClient('')
      await deleteSession(api, id)
    } catch {
      // 실패 시 롤백
      setSessions(initialSessions)
    }
  }

  return (
    <>
      <div className="mb-4 flex items-start justify-between">
        <PageHeading title={t('title')} accent="teal" />
        <div className="flex items-center gap-2">
          {sessions.length > 0 && (
            <Button variant="secondary" size="sm" onClick={() => setEditMode((v) => !v)}>
              {editMode ? t('editDone') : t('editToggle')}
            </Button>
          )}
          <Button size="sm" onClick={() => setSheetOpen(true)}>
            {t('newSession')}
          </Button>
        </div>
      </div>

      {sessions.length === 0 ? (
        <Card tone="soft" className="flex flex-col items-center gap-3 px-5 py-10 text-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/mascot.svg" alt="" width={64} height={64} />
          <p className="text-[15px] font-extrabold">{t('empty')}</p>
          <p className="text-sm text-c-text-sub">{t('emptyHint')}</p>
          <Button className="mt-1" onClick={() => setSheetOpen(true)}>
            {t('newSession')}
          </Button>
        </Card>
      ) : (
        <ul className="flex flex-col gap-3">
          {sessions.map((s) => (
            <li key={s.id}>
              <div className="flex items-center gap-2">
                <Link href={`/chat/${s.id}`} className="min-w-0 flex-1">
                  <Card className="flex items-center gap-3 p-3 transition-transform active:scale-[0.99]">
                    <span
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-c-text ${sessionColor(s.id)}`}
                    >
                      <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M4 6 a3 3 0 0 1 3-3 h10 a3 3 0 0 1 3 3 v7 a3 3 0 0 1-3 3 H10 l-4.5 4 v-4 H7 a3 3 0 0 1-3-3 Z" />
                      </svg>
                    </span>
                    <span className="min-w-0 flex-1 truncate text-[15px] font-extrabold text-c-text">
                      {s.title || t('sessionFallback')}
                    </span>
                    <span className="ml-2 shrink-0 text-xs font-semibold text-c-text-sub">
                      {formatDate(s.last_message_at, locale)}
                    </span>
                  </Card>
                </Link>
                {editMode && (
                  <button
                    className="shrink-0 rounded-full border border-c-line bg-c-surface p-2 text-c-text transition-opacity hover:opacity-70"
                    onClick={() => setDeletingSession(s)}
                    aria-label={t('deleteConfirm')}
                  >
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                      <path d="M10 11v6" />
                      <path d="M14 11v6" />
                      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
                    </svg>
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      <ChatEntrySheet
        open={sheetOpen}
        onClose={() => {
          setSheetOpen(false)
          setActivePrefill(null)
        }}
        profiles={profiles}
        prefill={activePrefill}
      />

      {deletingSession && (
        <DeleteModal
          sessionTitle={deletingSession.title || t('sessionFallback')}
          onConfirm={() => handleDelete(deletingSession.id)}
          onClose={() => setDeletingSession(null)}
          t={t}
        />
      )}
    </>
  )
}
