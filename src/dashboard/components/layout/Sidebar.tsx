"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "home" },
  { href: "/classes", label: "Classi", icon: "users" },
  { href: "/lessons", label: "Lezioni", icon: "book" },
  { href: "/alerts", label: "Alert", icon: "bell" },
] as const;

function NavIcon({ icon }: { icon: string }) {
  const common = { width: 20, height: 20, viewBox: "0 0 24 24", "aria-hidden": true as const, fill: "none", stroke: "currentColor", strokeWidth: 2 };
  switch (icon) {
    case "home":
      return <svg {...common}><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "users":
      return <svg {...common}><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "book":
      return <svg {...common}><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    case "bell":
      return <svg {...common}><path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" strokeLinecap="round" strokeLinejoin="round" /></svg>;
    default:
      return null;
  }
}

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav aria-label="Navigazione dashboard" className="flex h-full w-60 flex-col bg-surface-bg">
      <div className="flex items-center gap-2 border-b border-gray-200 px-4 py-4">
        <span className="text-lg font-bold text-page-fg">MAESTRO</span>
      </div>
      <ul className="mt-2 flex-1 space-y-1 px-2">
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus ${
                  isActive
                    ? "bg-focus/10 text-focus"
                    : "text-surface-fg hover:bg-gray-200"
                }`}
              >
                <NavIcon icon={item.icon} />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
