import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/Navbar';
export const metadata: Metadata = { title: 'ihui Systems — Core-Doc-Engine', description: 'Observabilidad y Documentación' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-bg text-text antialiased">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 pb-12">{children}</main>
      </body>
    </html>
  );
}
