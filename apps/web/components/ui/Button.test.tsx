import { describe, expect, it } from 'vitest'
import Button, { buttonClass } from './Button'

// Button은 훅 없는 순수 함수 컴포넌트라 직접 호출해 반환 엘리먼트의 props를 검사한다.
describe('Button', () => {
  it('type 기본값은 button이고 덮어쓸 수 있다', () => {
    expect(Button({ children: 'a' }).props.type).toBe('button')
    expect(Button({ type: 'submit', children: 'a' }).props.type).toBe('submit')
  })
  it('disabled 스타일과 danger 변형을 가진다', () => {
    expect(buttonClass()).toContain('disabled:opacity-50')
    expect(buttonClass()).toContain('disabled:active:scale-100')
    expect(buttonClass('danger')).toContain('bg-c-danger')
    expect(Button({ disabled: true, children: 'a' }).props.disabled).toBe(true)
  })
})
