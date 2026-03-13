/**
 * /auth/google — 백엔드 OAuth 시작점으로 전달 (리다이렉트 직접 따름 방지)
 *
 * Nuxt routeRules 프록시는 302를 서버 측에서 follow하므로
 * 브라우저가 Google 쿠키 없이 OAuth 페이지를 받는 문제 발생.
 * 이 라우트는 백엔드 응답의 Location 헤더만 추출해
 * 브라우저가 직접 accounts.google.com으로 이동하게 한다.
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendUrl = config.apiBase  // 서버 사이드 전용: http://backend:8000

  const res = await fetch(`${backendUrl}/api/auth/google`, {
    redirect: 'manual',
    headers: {
      cookie: getRequestHeader(event, 'cookie') ?? '',
    },
  })

  const location = res.headers.get('location')
  if (!location) {
    throw createError({ statusCode: 502, message: 'Backend did not return redirect' })
  }

  // 백엔드 세션 쿠키(authlib state) 브라우저에 전달
  for (const [key, value] of res.headers.entries()) {
    if (key.toLowerCase() === 'set-cookie') {
      appendResponseHeader(event, 'set-cookie', value)
    }
  }

  return sendRedirect(event, location, 302)
})
