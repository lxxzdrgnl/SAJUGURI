/**
 * /auth/google/callback — Google OAuth 콜백을 백엔드로 전달
 *
 * Google이 리다이렉트하는 경로. 쿼리 파라미터(code, state)와
 * 세션 쿠키를 백엔드로 전달하고, 백엔드가 반환하는
 * Location(프론트 /auth/callback?access_token=...) 으로 브라우저를 이동시킨다.
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendUrl = config.apiBase  // 서버 사이드 전용: http://backend:8000

  const query = getQuery(event)
  const qs = new URLSearchParams(query as Record<string, string>).toString()

  const res = await fetch(`${backendUrl}/api/auth/google/callback?${qs}`, {
    redirect: 'manual',
    headers: {
      cookie: getRequestHeader(event, 'cookie') ?? '',
    },
  })

  const location = res.headers.get('location')
  if (!location) {
    throw createError({ statusCode: 502, message: 'Backend callback failed' })
  }

  return sendRedirect(event, location, 302)
})
