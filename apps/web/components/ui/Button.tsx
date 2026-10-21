import type { ButtonHTMLAttributes } from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost'
export type ButtonSize = 'sm' | 'md'

const VARIANT: Record<ButtonVariant, string> = {
  primary: 'bg-c-accent text-c-on-accent',
  secondary: 'bg-c-surface text-c-text border border-c-line',
  ghost: 'bg-transparent text-c-text',
}

const SIZE: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-11 px-5 text-sm',
}

/** Link 등 다른 요소에서 버튼 모양을 쓸 때 같은 클래스를 얻는다 */
export function buttonClass(variant: ButtonVariant = 'primary', size: ButtonSize = 'md'): string {
  return [
    'inline-flex items-center justify-center gap-1.5 rounded-pill font-extrabold',
    'transition-transform duration-(--motion-duration-press) active:scale-[0.98]',
    VARIANT[variant],
    SIZE[size],
  ].join(' ')
}

export default function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; size?: ButtonSize }) {
  return <button className={`${buttonClass(variant, size)} ${className}`.trim()} {...rest} />
}
