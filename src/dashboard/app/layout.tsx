import type { Metadata } from "next";
import "./globals.css";
import ClientLayout from "./client-layout";

export const metadata: Metadata = {
  title: "Dashboard Docente - MAESTRO",
  description: "Dashboard per il docente - MAESTRO Personalised Learning Companion",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="bg-page-bg text-page-fg">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
