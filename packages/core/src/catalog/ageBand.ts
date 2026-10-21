export function ageBand(birthDate: string, today: Date): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(birthDate)
  if (!m) return null
  const y = Number(m[1])
  const mo = Number(m[2])
  const d = Number(m[3])
  const dt = new Date(Date.UTC(y, mo - 1, d))
  if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) return null
  const tm = today.getMonth() + 1
  const td = today.getDate()
  let age = today.getFullYear() - y
  if (tm < mo || (tm === mo && td < d)) age -= 1
  if (age < 0) return null
  const lo = Math.floor(age / 5) * 5
  return `${lo}-${lo + 4}`
}
