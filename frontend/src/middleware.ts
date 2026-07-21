import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedRoutes = [
  "/dashboard",
  "/select-institution",
  "/colleges",
  "/departments",
  "/teachers",
  "/subjects",
  "/classrooms",
  "/laboratories",
  "/time-slots",
  "/calendar",
  "/constraints",
  "/timetables",
  "/import",
  "/export",
  "/analytics",
  "/insights",
  "/health-score",
  "/simulation",
  "/versions",
  "/approvals",
  "/audit-logs",
  "/notifications",
  "/search",
  "/settings",
  "/profile",
  "/sections",
  "/semesters",
  "/conflicts",
];

const publicRoutes = ["/login", "/forgot-password", "/", "/_not-found"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  if ((pathname === "/login" || pathname === "/forgot-password") && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.svg$).*)",
  ],
};
