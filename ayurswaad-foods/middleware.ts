import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
import { NextRequest, NextResponse } from 'next/server';
import { verifyJWT } from '@/lib/jwt';

const intlMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Auth Logic
  const isProtectedRoute =
    pathname.includes('/admin') ||
    pathname.includes('/user');
    // pathname.includes('/checkout') || // Temporarily disabled for checkout to debug middleware issue

  if (isProtectedRoute) {
    const token = request.cookies.get('token')?.value;
    // verifyJWT is edge-compatible (uses jose)
    const session = token ? await verifyJWT(token) : null;

    if (!session) {
      // Redirect to login
      // We need to know the locale to redirect correctly
      const locale = pathname.match(/^\/(en|hi)/)?.[1] || 'en';
      return NextResponse.redirect(new URL(`/${locale}/login`, request.url));
    }

    if (pathname.includes('/admin') && (session as any).role !== 'ADMIN') {
      const locale = pathname.match(/^\/(en|hi)/)?.[1] || 'en';
      return NextResponse.redirect(new URL(`/${locale}/`, request.url));
    }
  }

  // Run internationalization middleware last so it handles locale detection/rewrites properly
  return intlMiddleware(request);
}

export const config = {
  matcher: ['/', '/(hi|en)/:path*']
};
