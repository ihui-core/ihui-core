"use client";

import { useEffect, useState } from "react";

type Status = "VERIFICADO" | "NO_ENCONTRADO" | "DISCREPANCIA" | "NO_VERIFICABLE";

async function loadJson(path: string): Promise<any[]> {
  try {
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

// Verde SOLO con VERIFICADO. Todo lo demas nunca se pinta como exito.
function Badge({ status }: { status?: string }) {
  const s = (status || "SIN_DATO") as Status | "SIN_DATO";
  const styles: Record<string, string> = {
    VERIFICADO: "bg-emerald-950 text-emerald-300 border-emerald-800",
    DISCREPANCIA: "bg-red-950 text-red-300 border-red-800",
    NO_ENCONTRADO: "bg-amber-950 text-amber-300 border-amber-800",
    NO_VERIFICABLE: "bg-slate-800 text-slate-400 border-slate-600",
    SIN_DATO: "bg-slate-800 text-slate-400 border-slate-600",
  };
  return (
    <span className={`inline-block px-2 py-0.5 text-xs font-mono border rounded ${styles[s] || styles.SIN_DATO}`}>
      {s}
    </span>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="text-slate-500 font-mono text-sm py-8">{children}</div>;
}

export default function Dashboard() {
  const [tab, setTab] = useState("feed");
  const [sessions, setSessions] = useState<any[]>([]);
  const [git, setGit] = useState<any[]>([]);
  const [adrs, setAdrs] = useState<any[]>([]);
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      loadJson("/data/sessions.json"),
      loadJson("/data/git_activity.json"),
      loadJson("/data/adrs.json"),
      loadJson("/data/docs.json"),
    ]).then(([s, g, a, d]) => {
      setSessions(s);
      setGit(g);
      setAdrs(a);
      setDocs(d);
      setLoading(false);
    });
  }, []);

  const tabs = [
    { id: "feed", label: "Feed Diario" },
    { id: "adrs", label: "ADR Guardian" },
    { id: "git", label: "Actividad Git" },
    { id: "docs", label: "Documentacion" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <header className="border-b border-slate-800 px-6 py-4">
        <h1 className="text-lg font-semibold">ihui Core-Doc-Engine v1</h1>
        <p className="text-xs text-slate-500 font-mono mt-1">
          Claims verificados contra el historial de Git. Verde solo con evidencia.
        </p>
      </header>

      <nav className="border-b border-slate-800 px-6 flex gap-6">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`py-3 text-sm border-b-2 -mb-px transition ${
              tab === t.id
                ? "border-slate-200 text-slate-100"
                : "border-transparent text-slate-500 hover:text-slate-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="px-6 py-6 max-w-5xl">
        {loading && <Empty>Cargando datos estaticos...</Empty>}

        {!loading && tab === "feed" && (
          <div className="space-y-4">
            {sessions.length === 0 && <Empty>[FALTA SESIONES] No hay registros en .sessions/</Empty>}
            {sessions.map((s, i) => {
              const v = s.verification || {};
              const d = v.details || {};
              return (
                <div key={i} className="border border-slate-800 rounded p-4">
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className="font-mono text-sm text-slate-100">{s.agent_id}</span>
                    <span className="font-mono text-xs text-slate-500">{s.branch}</span>
                    <span className="font-mono text-xs text-slate-500">{s.outcome}</span>
                    <Badge status={v.status} />
                  </div>
                  <p className="text-sm text-slate-400 mt-2">{s.summary}</p>
                  <div className="mt-3 space-y-1">
                    {(d.files || []).map((f: any, j: number) => (
                      <div key={j} className="flex items-center gap-2 text-xs font-mono">
                        <Badge status={f.status} />
                        <span className="text-slate-400">{f.file}</span>
                      </div>
                    ))}
                    {(d.adrs || []).map((a: any, j: number) => (
                      <div key={j} className="flex items-center gap-2 text-xs font-mono">
                        <Badge status={a.status} />
                        <span className="text-slate-400">{a.adr}</span>
                      </div>
                    ))}
                    {(d.prs || []).map((p: any, j: number) => (
                      <div key={j} className="flex items-center gap-2 text-xs font-mono">
                        <Badge status={p.status} />
                        <span className="text-slate-400">PR #{p.number}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!loading && tab === "adrs" && (
          <div className="space-y-3">
            {adrs.length === 0 && <Empty>[FALTA ADRS] No se encontro el archivo maestro de ADRs.</Empty>}
            {adrs.map((a, i) => (
              <div key={i} className="border border-slate-800 rounded p-4">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="font-mono text-sm text-slate-100">{a.numero || a.number}</span>
                  <span className="text-sm">{a.titulo || a.title}</span>
                </div>
                <div className="text-xs font-mono text-slate-500 mt-2">
                  Declarado: {a.estado_declarado || a.declared_status || "[FALTA]"} · Detectado:{" "}
                  {a.estado_detectado || a.auto_status || "[FALTA]"}
                </div>
                <div className="text-xs font-mono text-slate-500 mt-1">
                  Evidencia:{" "}
                  {(a.commits_vinculados || []).length > 0
                    ? (a.commits_vinculados || []).join(", ")
                    : "Ninguna (sin trailer ADR: NNN)"}
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && tab === "git" && (
          <div className="space-y-2">
            {git.length === 0 && <Empty>[FALTA GIT] Sin commits leidos.</Empty>}
            {git.map((c, i) => (
              <div key={i} className="border border-slate-800 rounded p-3 text-xs font-mono">
                <span className="text-slate-500">{c.hash}</span>{" "}
                <span className="text-slate-300">{c.subject}</span>
                <div className="text-slate-600 mt-1">
                  {c.author} · {c.date}
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && tab === "docs" && (
          <div className="space-y-4">
            {docs.length === 0 && <Empty>[FALTA DOCS] No se encontro PROJECTBRAIN/</Empty>}
            {docs.map((d, i) => (
              <details key={i} className="border border-slate-800 rounded p-4">
                <summary className="cursor-pointer text-sm text-slate-200">{d.title}</summary>
                <div className="text-xs font-mono text-slate-500 mt-1">{d.path}</div>
                <div
                  className="prose prose-invert prose-sm max-w-none mt-4"
                  dangerouslySetInnerHTML={{ __html: d.html }}
                />
              </details>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
