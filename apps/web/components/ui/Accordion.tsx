'use client'

import { useState, type ReactNode } from 'react'

/** 접이식 카드 — 1px 라인 카드, 펼치면 본문색 라인으로 강조. 이모지 금지, SVG 셰브론 */
export default function Accordion({
  title,
  defaultOpen = false,
  children,
}: {
  title: ReactNode
  defaultOpen?: boolean
  children: ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div
      className={`overflow-hidden rounded-card border bg-c-surface ${
        open ? 'border-c-text' : 'border-c-line'
      }`}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className={`flex w-full items-center justify-between px-5 py-4 text-left text-[14px] font-extrabold ${
          open ? 'text-c-text' : 'text-c-text-sub'
        }`}
      >
        {title}
        <svg
          className={`h-4 w-4 shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
          viewBox="0 0 16 16"
          fill="none"
          aria-hidden="true"
        >
          <path d="M4 6l4 4 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && <div className="border-t border-c-line px-5 py-4">{children}</div>}
    </div>
  )
}
