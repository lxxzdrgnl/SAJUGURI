'use client'

import { useRef, useState, type ReactNode } from 'react'

/** CSS scroll-snap 가로 슬라이드 + 페이지 점. 자동 넘김 없음. */
export default function HeroCarousel({ slides }: { slides: ReactNode[] }) {
  const rowRef = useRef<HTMLDivElement>(null)
  const [index, setIndex] = useState(0)

  const onScroll = () => {
    const el = rowRef.current
    if (!el || el.clientWidth === 0) return
    setIndex(Math.round(el.scrollLeft / el.clientWidth))
  }

  return (
    <div>
      <div
        ref={rowRef}
        onScroll={onScroll}
        className="flex snap-x snap-mandatory overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {slides.map((slide, i) => (
          <div key={i} className="w-full shrink-0 snap-center">
            {slide}
          </div>
        ))}
      </div>
      {slides.length > 1 && (
        <div className="mt-3 flex justify-center gap-1.5" aria-hidden>
          {slides.map((_, i) => (
            <span
              key={i}
              className={`h-1.5 rounded-pill transition-all ${i === index ? 'w-4 bg-c-accent' : 'w-1.5 bg-c-line'}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
