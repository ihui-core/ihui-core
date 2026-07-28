'use client';
import { useEffect, useState } from 'react';
import { DocItem } from '@/types/docengine';
export default function DocsPage() {
  const [docs, setDocs] = useState<DocItem[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { fetch('/data/docs.json').then(res => res.json()).then(data => { setDocs(data.docs || []); setLoading(false); }).catch(() => setLoading(false)); }, []);
  if (loading) return <div className="p-8 text-muted font-mono">[CARGANDO DOCUMENTOS...]</div>;
  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold tracking-tight">Documentación Viva</h1></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {docs.length === 0 ? <div className="p-8 border border-border bg-surface text-center text-muted font-mono col-span-2">[FALTA DOCS]</div> : docs.map((doc, idx) => (
          <div key={idx} className={`border p-4 rounded-lg bg-surface space-y-2 transition-colors ${doc.is_stale ? 'border-warn bg-yellow-950/20' : 'border-border'}`}>
            <h2 className="font-bold text-text text-base">{doc.title}</h2>
            <p className="text-xs text-muted font-mono mt-0.5">{doc.path}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
