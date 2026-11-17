import { NextResponse } from 'next/server'

function parseCookies(cookieHeader: string | null): { [key: string]: string } {
  if (!cookieHeader) return {}
  return cookieHeader
    .split(';')
    .reduce((acc, curr) => {
      const [key, ...value] = curr.split('=')
      if (key && value.length > 0) {
        acc[key.trim()] = value.join('=').trim()
      }
      return acc
    }, {} as { [key: string]: string })
}

export function middleware(request: { nextUrl: URL; headers: { get: (key: string) => string } }) {
  const { pathname } = request.nextUrl
  const cookies = parseCookies(request.headers.get('cookie') || '')

  const isProtected = pathname.startsWith('/dashboard') || pathname.startsWith('/missions/')
  const isAuthRoute = pathname.startsWith('/login') || pathname.startsWith('/auth')

  const accessToken = cookies.access_token
  const refreshToken = cookies.refresh_token

  if (isProtected && !accessToken) {
    const loginUrl = new URL('/login', request.nextUrl.origin)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isProtected && accessToken) {
    const res = NextResponse.next()
    res.headers.set('Authorization', `Bearer ${accessToken}`)
    return res
  }

  if (!isAuthRoute && !accessToken) {
    const loginUrl = new URL('/login', request.nextUrl.origin)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}