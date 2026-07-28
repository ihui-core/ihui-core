'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
export function Navbar() {
  const pathname = usePathname();
  const navItems = [
    { label: 'Feed Diario', href: '/' },
    { label: 'ADR Guardian', href: '/adrs/' },
    { label: 'Actividad Git', href: '/git/' },
    { label: 'Documentación', href: '/docs/' },
  ];
  return (
    <header className="border-b border-border bg-surface px-6 py-4 mb-8">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <span className="font-bold text-xl text-accent tracking-wider">ihui</span>
          <span className="text-muted text-sm border-l border-border pl-3">Core-Doc-Engine v1</span>
        </div>
        <nav className="flex space-x-6">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className={`text-sm font-medium transition-colors ${ pathname === item.href ? 'text-accent border-b-2 border-accent pb-1' : 'text-muted hover:text-text' }`}>{item.label}</Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
