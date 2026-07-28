"use client";

import { useEffect, useState } from "react";

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

// Verde SOLO con VERIFICADO. Nada mas se pinta como exito.
const MEANING: Record<string, { label: string; plain: string; cls: string; dot: string }> = {
  VERIFICADO: {
    label: "Confirmado",
    plain: "Git confirma que esto pasó",
    cls: "bg-emerald-950/60 text-emerald-300 border-emerald-800",
    dot: "bg-emerald-400",
  },
  NO_ENCONTRADO: {
    label: "No aparece",
    plain: "Lo declaró, pero no está en los commits",
    cls: "bg-amber-950/60 text-amber-300 border-amber-800",
    dot: "bg-amber-400",
  },
  DISCREPANCIA: {
    label: "Sin declarar",
    plain: "Cambió esto y no lo reportó",
    cls: "bg-red-950/60 text-red-300 border-red-800",
    dot: "bg-red-400",
  },
  NO_VERIFICABLE: {
    label: "Sin comprobar",
    plain: "El motor no pudo revisarlo",
    cls: "bg-slate-800 text-slate-400 border-slate-600",
    dot: "bg-slate-500",
  },
};

function meta(status?: string) {
  return MEANING[status || ""] || MEANING.NO_VERIFICABLE;
}

function Pill({ status }: { status?: string }) {
  const m = meta(status);
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs border rounded-full ${m.cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${m.dot}`} />
      {m.label}
    </span>
  );
}

function fmt(iso?: string) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString("es-MX", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function verdict(status: string, counts: Record<string, number>) {
  if (status === "VERIFICADO") return "Todo lo que reportó, Git lo confirma.";
  if (status === "DISCREPANCIA")
    return `Tocó ${counts.DISCREPANCIA} archivo(s) que no reportó. Revisa qué más cambió.`;
  if (status === "NO_ENCONTRADO")
    return `Reportó ${counts.NO_ENCONTRADO} cosa(s) que no aparecen en los commits.`;
  return "No se pudo comprobar. Falta historial, token o el rango salió vacío.";
}

function Empty({ children }: { children: React.ReactNode }) {
  return (
    <div className="border border-dashed border-slate-700 rounded-lg p-8 text-center text-slate-500 text-sm">
      {children}
    </div>
  );
}

export default function Dashboard() {
  const [tab, setTab] = useState("feed");
  const [sessions, setSessions] = useState<any[]>([]);
  const [git, setGit] = useState<any[]>([]);
  const [adrs, setAdrs] = useState<any[]>([]);
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<Record<number, boolean>>({});

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
    { id: "feed", label: "Sesiones" },
    { id: "adrs", label: "ADRs" },
    { id: "git", label: "Commits" },
    { id: "docs", label: "Documentos" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-xl font-semibold text-slate-100">Core-Doc-Engine</h1>
        <p className="text-sm text-slate-400 mt-1">
          Cada agente reporta lo que hizo. Aquí se contrasta contra Git.
        </p>
      </header>

      <nav className="border-b border-slate-800 px-6 flex gap-6 sticky top-0 bg-slate-950 z-10">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`py-3 text-sm border-b-2 -mb-px transition ${
              tab === t.id
                ? "border-slate-100 text-slate-100 font-medium"
                : "border-transparent text-slate-500 hover:text-slate-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="px-6 py-6 max-w-4xl mx-auto">
        {loading && <Empty>Cargando…</Empty>}

        {!loading && tab === "feed" && (
          <>
            <div className="flex flex-wrap gap-4 mb-6 text-xs text-slate-500">
              {Object.entries(MEANING).map(([k, m]) => (
                <div key={k} className="flex items-center gap-1.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${m.dot}`} />
                  <span className="text-slate-400">{m.label}:</span>
                  <span>{m.plain}</span>
                </div>
              ))}
            </div>

            <div className="space-y-5">
              {sessions.length === 0 && (
                <Empty>No hay sesiones registradas. Los agentes escriben en .sessions/</Empty>
              )}

              {sessions.map((s, i) => {
                const v = s.verification || {};
                const d = v.details || {};
                const files = d.files || [];
                const declared = files.filter((f: any) => f.status !== "DISCREPANCIA");
                const undeclared = files.filter((f: any) => f.status === "DISCREPANCIA");
                const counts: Record<string, number> = {};
                [...files, ...(d.adrs || []), ...(d.prs || [])].forEach((x: any) => {
                  counts[x.status] = (counts[x.status] || 0) + 1;
                });

                return (
                  <article key={i} className="border border-slate-800 rounded-lg overflow-hidden">
                    <div className="p-4 bg-slate-900/40">
                      <div className="flex items-start justify-between gap-4 flex-wrap">
                        <div>
                          <div className="text-base font-medium text-slate-100">{s.agent_id}</div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            rama {s.branch} · {fmt(s.started_at)} → {fmt(s.ended_at)}
                          </div>
                        </div>
                        <Pill status={v.status} />
                      </div>

                      <p className="text-sm text-slate-300 mt-3">{s.summary}</p>

                      <p className="text-sm text-slate-400 mt-2 border-l-2 border-slate-700 pl-3">
                        {verdict(v.status, counts)}
                      </p>
                    </div>

                    <div className="p-4 space-y-4">
                      <section>
                        <h3 className="text-xs uppercase tracking-wide text-slate-500 mb-2">
                          Lo que reportó
                        </h3>
                        {declared.length === 0 && (d.adrs || []).length === 0 && (d.prs || []).length === 0 && (
                          <p className="text-sm text-slate-600">Nada.</p>
                        )}
                        <ul className="space-y-1.5">
                          {declared.map((f: any, j: number) => (
                            <li key={j} className="flex items-center gap-2.5 text-sm">
                              <Pill status={f.status} />
                              <span className="text-slate-400 font-mono text-xs break-all">{f.file}</span>
                            </li>
                          ))}
                          {(d.adrs || []).map((a: any, j: number) => (
                            <li key={`a${j}`} className="flex items-center gap-2.5 text-sm">
                              <Pill status={a.status} />
                              <span className="text-slate-400 font-mono text-xs">{a.adr}</span>
                            </li>
                          ))}
                          {(d.prs || []).map((p: any, j: number) => (
                            <li key={`p${j}`} className="flex items-center gap-2.5 text-sm">
                              <Pill status={p.status} />
                              <span className="text-slate-400 font-mono text-xs">PR #{p.number}</span>
                            </li>
                          ))}
                        </ul>
                      </section>

                      {undeclared.length > 0 && (
                        <section>
                          <button
                            onClick={() => setOpen({ ...open, [i]: !open[i] })}
                            className="w-full text-left flex items-center justify-between gap-3 bg-red-950/30 border border-red-900/50 rounded px-3 py-2.5 hover:bg-red-950/50 transition"
                          >
                            <span className="text-sm text-red-300">
                              {undeclared.length} archivos cambiaron sin que los reportara
                            </span>
                            <span className="text-xs text-red-400/70">
                              {open[i] ? "ocultar" : "ver"}
                            </span>
                          </button>
                          {open[i] && (
                            <ul className="mt-2 space-y-1 pl-3 border-l border-red-900/50">
                              {undeclared.map((f: any, j: number) => (
                                <li key={j} className="text-xs font-mono text-slate-500 break-all">
                                  {f.file}
                                </li>
                              ))}
                            </ul>
                          )}
                        </section>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </>
        )}

        {!loading && tab === "adrs" && (
          <div className="space-y-3">
            {adrs.length === 0 && (
              <Empty>
                No se encontró el archivo maestro de ADRs.
                <br />
                <span className="text-xs">Revisa la ruta ADRS_MASTER_PATH en generate.py</span>
              </Empty>
            )}
            {adrs.map((a, i) => {
              const commits = a.commits_vinculados || [];
              return (
                <div key={i} className="border border-slate-800 rounded-lg p-4">
                  <div className="flex items-baseline gap-3 flex-wrap">
                    <span className="font-mono text-sm text-slate-300">{a.numero || a.number}</span>
                    <span className="text-sm text-slate-100">{a.titulo || a.title}</span>
                  </div>
                  <div className="text-sm text-slate-400 mt-2">
                    Dice estar: <span className="text-slate-200">{a.estado_declarado || "—"}</span>
                    {" · "}
                    Git sugiere:{" "}
                    <span className="text-slate-200">{a.estado_detectado || "sin evidencia"}</span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    {commits.length > 0
                      ? `Respaldado por ${commits.length} commit(s): ${commits.join(", ")}`
                      : "Ningún commit lo menciona (falta el trailer ADR: NNN)"}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!loading && tab === "git" && (
          <div className="space-y-2">
            {git.length === 0 && <Empty>Sin commits leídos.</Empty>}
            {git.map((c, i) => (
              <div key={i} className="border border-slate-800 rounded-lg p-3">
                <div className="text-sm text-slate-200">{c.subject}</div>
                <div className="text-xs text-slate-500 mt-1 font-mono">
                  {c.hash} · {c.author} · {c.date}
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && tab === "docs" && (
          <div className="space-y-3">
            {docs.length === 0 && <Empty>No se encontró la carpeta PROJECTBRAIN.</Empty>}
            {docs.map((d, i) => (
              <details key={i} className="border border-slate-800 rounded-lg p-4">
                <summary className="cursor-pointer text-sm text-slate-200">{d.title}</summary>
                <div className="text-xs font-mono text-slate-600 mt-1">{d.path}</div>
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
