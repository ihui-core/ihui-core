'use client';
import { useEffect, useState } from 'react';
import { AgentSession, InvalidSession } from '@/types/docengine';
import { StatusBadge } from '@/components/StatusBadge';
import { ClaimsViewer } from '@/components/ClaimsViewer';
export default function FeedPage() {
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [invalidSessions, setInvalidSessions] = useState<InvalidSession[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch('/data/sessions.json').then(res => res.json()).then(data => {
      setSessions(data.sessions || []); setInvalidSessions(data.invalid_sessions || []); setLoading(false);
    }).catch(() => setLoading(false));
  }, []);
  if (loading) return <div className="p-8 text-muted font-mono">[CARGANDO SESIONES...]</div>;
  return (
    <div className="space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">Feed Diario de Sesiones</h1><p className="text-muted text-sm mt-1">Claims verificados determinísticamente contra Git.</p></div>
      {invalidSessions.length > 0 && (
        <div className="border border-error bg-red-950/40 p-4 rounded-lg space-y-2">
          <h2 className="text-error font-bold uppercase tracking-wider text-sm flex items-center space-x-2"><span>[FALTA VALIDACIÓN ESQUEMA] Inválidos: {invalidSessions.length}</span></h2>
          <div className="space-y-1">{invalidSessions.map((inv, idx) => <div key={idx} className="text-xs font-mono text-error/90">• <span className="font-semibold">{inv.file_name}</span>: {inv.error}</div>)}</div>
        </div>
      )}
      <div className="space-y-4">
        {sessions.length === 0 ? <div className="p-8 border border-border bg-surface text-center text-muted">[FALTA SESIONES]</div> : sessions.map(s => (
          <div key={s.session_id} className="border border-border bg-surface p-5 rounded-lg space-y-3">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <div className="flex items-center space-x-3">
                  <span className="font-bold text-accent text-base">{s.agent_id}</span>
                  <span className="text-xs bg-bg border border-border px-2 py-0.5 rounded font-mono text-muted">{s.branch}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2"><StatusBadge status={s.outcome} />{s.verification && <StatusBadge status={s.verification.status} />}</div>
            </div>
            <div className="text-sm bg-bg/50 p-3 rounded border border-border font-mono">{s.summary}</div>
            <ClaimsViewer claims={s.claims} verificationDetails={s.verification?.details} />
          </div>
        ))}
      </div>
    </div>
  );
}
