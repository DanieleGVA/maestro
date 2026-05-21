import { NextRequest, NextResponse } from "next/server";

/**
 * Next.js Edge Middleware: protects all dashboard routes.
 * Checks for 'maestro_token' cookie presence and basic JWT expiry.
 * Unauthenticated requests are redirected to /login.
 *
 * NOTE: This runs on the Edge Runtime -- no Node.js APIs available.
 * Full token signature verification happens server-side / in the API layer.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that do not require authentication
  if (
    pathname === "/login" ||
    pathname.startsWith("/_next") ||
    pathname === "/favicon.ico" ||
    pathname.startsWith("/api")
  ) {
    return NextResponse.next();
  }

  const token = request.cookies.get("maestro_token")?.value;

  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Basic expiry check (decode JWT payload without verification)
  try {
    const payloadB64 = token.split(".")[1];
    if (!payloadB64) {
      return redirectToLogin(request, pathname);
    }
    const payload = JSON.parse(atob(payloadB64));
    if (typeof payload.exp === "number" && payload.exp * 1000 < Date.now()) {
      // Token expired -- clear cookie and redirect
      const response = NextResponse.redirect(new URL("/login", request.url));
      response.cookies.delete("maestro_token");
      return response;
    }
  } catch {
    // Malformed token -- clear and redirect
    const response = NextResponse.redirect(new URL("/login", request.url));
    response.cookies.delete("maestro_token");
    return response;
  }

  return NextResponse.next();
}

function redirectToLogin(request: NextRequest, pathname: string): NextResponse {
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("redirect", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
