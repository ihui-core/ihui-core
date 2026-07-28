'use client';
import { useEffect, useState } from 'react';
import { GitCommit } from '@/types/docengine';
export default function GitActivityPage() {
  const [commits, setCommits] = useState<GitCommit[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { fetch('/data/git_activity.json').then(res => res.json()).then(data => { setCommits(data.main_commits || []); setLoading(false); }).catch(() => setLoading(false)); }, []);
  if (loading) return <div className="p-8 text-muted font-mono">[CARGANDO ACTIVIDAD GIT...]</div>;
  return (
    <div className="space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">Actividad Git</h1></div>
      <div className="border border-border bg-surface p-5 rounded-lg space-y-4">
        <h2 className="font-bold uppercase text-xs font-mono text-muted border-b border-border pb-2">Commits Recientes en main</h2>
        <div className="space-y-3 font-mono text-xs">
          {commits.map(c => (
            <div key={c.sha} className="bg-bg p-3 rounded border border-border space-y-1">
              <div className="flex justify-between items-center"><span className="text-accent font-bold">{c.sha.substring(0, 7)}</span></div>
              <div className="text-text font-sans text-sm">{c.message}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
