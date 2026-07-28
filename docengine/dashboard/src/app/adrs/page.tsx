'use client';
import { useEffect, useState } from 'react';
import { ADRItem } from '@/types/docengine';
export default function ADRPage() {
  const [adrs, setAdrs] = useState<ADRItem[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { fetch('/data/adrs.json').then(res => res.json()).then(data => { setAdrs(data.adrs || []); setLoading(false); }).catch(() => setLoading(false)); }, []);
  if (loading) return <div className="p-8 text-muted font-mono">[CARGANDO ADRS...]</div>;
  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold tracking-tight">ADR Guardian</h1></div>
      <div className="border border-border rounded-lg overflow-hidden bg-surface">
        <table className="w-full text-left text-xs">
          <thead className="bg-bg border-b border-border uppercase font-mono text-muted"><tr><th className="p-4">ADR</th><th className="p-4">Título</th><th className="p-4">Estado Declarado</th><th className="p-4">Auto-Detección CI</th></tr></thead>
          <tbody className="divide-y divide-border">
            {adrs.length === 0 ? <tr><td colSpan={4} className="p-6 text-center text-muted font-mono">[FALTA ADRS]</td></tr> : adrs.map(adr => (
              <tr key={adr.id} className="hover:bg-bg/40 transition-colors">
                <td className="p-4 font-bold font-mono text-accent">{adr.id}</td>
                <td className="p-4 font-semibold text-text">{adr.title}</td>
                <td className="p-4"><span className="px-2 py-1 bg-bg border border-border rounded text-muted">{adr.declared_status}</span></td>
                <td className="p-4"><span className={`px-2 py-1 rounded font-bold ${adr.auto_status.includes('auto-detectado') ? 'bg-blue-950 text-accent border border-accent' : 'bg-bg text-muted'}`}>{adr.auto_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
