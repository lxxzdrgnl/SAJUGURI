import { POOL, paletteFromBase } from '@/lib/fortune/story'

/**
 * 운세 스토리 배경 팔레트 검토 페이지 (/palette).
 * 풀의 모든 비비드 색을 배경 + 샘플 헤드라인/본문으로 렌더해 가독성·분위기를 확인한다.
 */
const SEMANTIC = [
  ['c-bg', 'bg-c-bg'],
  ['c-surface', 'bg-c-surface'],
  ['c-surface-soft', 'bg-c-surface-soft'],
  ['c-line', 'bg-c-line'],
  ['c-text', 'bg-c-text'],
  ['c-text-sub', 'bg-c-text-sub'],
  ['c-accent', 'bg-c-accent'],
  ['c-danger', 'bg-c-danger'],
  ['c-counsel-bg', 'bg-c-counsel-bg'],
  ['c-scrim', 'bg-c-scrim'],
] as const

const POSTER = [
  ['butter', 'bg-c-poster-butter'],
  ['rose', 'bg-c-poster-rose'],
  ['lilac', 'bg-c-poster-lilac'],
  ['peach', 'bg-c-poster-peach'],
  ['sky', 'bg-c-poster-sky'],
  ['mint', 'bg-c-poster-mint'],
] as const

export default function PaletteReviewPage() {
  return (
    <main className="-mx-4 -mt-4 flex min-h-dvh flex-col gap-4 bg-c-bg px-4 pb-10 pt-6 text-c-text">
      <section>
        <h2 className="font-display text-xl font-normal">시맨틱 토큰</h2>
        <ul className="mt-3 grid grid-cols-2 gap-2">
          {SEMANTIC.map(([name, cls]) => (
            <li key={name} className="flex items-center gap-2 rounded-card border border-c-line bg-c-surface p-2">
              <span className={`h-8 w-8 shrink-0 rounded-full border border-c-line ${cls}`} />
              <span className="min-w-0 truncate text-xs text-c-text-sub">--{name}</span>
            </li>
          ))}
        </ul>
        <h2 className="mt-5 font-display text-xl font-normal">포스터 팔레트</h2>
        <ul className="mt-3 grid grid-cols-3 gap-2">
          {POSTER.map(([n, cls]) => (
            <li key={n} className="overflow-hidden rounded-card border border-c-line bg-c-surface">
              <span className={`block h-14 ${cls}`} />
              <span className="block px-2 py-1.5 text-xs text-c-text-sub">poster-{n}</span>
            </li>
          ))}
        </ul>
      </section>

      <div>
        <h1 className="font-display text-xl font-normal leading-tight">운세 배경 팔레트 검토</h1>
        <span className="mt-2 block h-1 w-12 rounded-pill bg-c-accent" />
        <p className="mt-2 text-[13px] text-c-text-sub">
          총 {POOL.length}색. 운세마다(날짜+간지+이름) 셔플되어 한 운세 안에서는 색이 겹치지 않습니다.
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {POOL.map((hex, i) => {
          const p = paletteFromBase(hex)
          return (
            <div
              key={hex}
              className="overflow-hidden rounded-card border border-c-line p-6"
              style={{ background: p.bg }}
            >
              <div
                className="mb-2 text-[13px] font-black tabular-nums"
                style={{ color: p.accent }}
              >
                {String(i + 1).padStart(2, '0')} · {hex}
              </div>
              <h2
                className="text-[24px] font-black leading-tight"
                style={{ color: p.ink, wordBreak: 'keep-all' }}
              >
                오늘은 흐름이 잘 받쳐주는 날
              </h2>
              <p
                className="mt-2 text-[15px] leading-relaxed"
                style={{ color: p.inkSoft, wordBreak: 'keep-all' }}
              >
                이 배경 위에서 헤드라인과 본문 글씨가 또렷하게 읽히는지, 분위기가 좋은지 확인해 주세요.
                포인트 색(번호)도 함께 봅니다.
              </p>
            </div>
          )
        })}
      </div>
    </main>
  )
}
