"use client";

// Codificado por Claude · Core-Doc-Engine (ihui Systems) · 2026
// Las vistas Universo/Proyecto/Contrato/Versiones implementan la maqueta
// congelada tablero_docengine_spec_congelado.html (la spec, no una propuesta),
// integradas al tema oscuro existente. Ningún número de este tablero se
// teclea: todo sale de tracker.json / historial.json, generados por el motor.

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

async function loadObj(path: string): Promise<any | null> {
  try {
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    return data && typeof data === "object" && !Array.isArray(data) ? data : null;
  } catch {
    return null;
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

// ---------- piezas de las vistas congeladas (tema oscuro) ----------

const PRIO_CLS: Record<string, string> = {
  P0: "bg-red-950/60 text-red-300 border-red-800",
  P1: "bg-orange-950/60 text-orange-300 border-orange-800",
  P2: "bg-amber-950/60 text-amber-300 border-amber-800",
  P3: "bg-slate-800 text-slate-400 border-slate-600",
};

function Tile({ num, lbl, tone }: { num: React.ReactNode; lbl: string; tone?: string }) {
  const color =
    tone === "red" ? "text-red-400" : tone === "base" ? "text-blue-400" : tone === "exp" ? "text-cyan-400" : "text-slate-100";
  return (
    <div className="border border-slate-800 rounded-xl p-4 bg-slate-900/40">
      <div className={`text-2xl font-bold tracking-tight ${color}`}>{num}</div>
      <div className="text-[11px] uppercase tracking-wide text-slate-500 mt-1">{lbl}</div>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border border-slate-800 rounded-xl p-4 bg-slate-900/40 mb-4">
      <h2 className="text-xs uppercase tracking-wide text-slate-500 mb-3">{title}</h2>
      {children}
    </div>
  );
}

function StackBar({ segs }: { segs: { w: number; cls: string; label: string }[] }) {
  const visible = segs.filter((s) => s.w > 0);
  return (
    <div className="flex h-8 rounded-lg overflow-hidden border border-slate-800 bg-slate-800/50">
      {visible.map((s, i) => (
        <span
          key={i}
          style={{ width: `${s.w}%` }}
          className={`flex items-center justify-center text-[11px] font-semibold text-white whitespace-nowrap overflow-hidden ${s.cls}`}
        >
          {s.label}
        </span>
      ))}
    </div>
  );
}

function BarRow({ label, n, max, cls, empty }: { label: string; n: number; max: number; cls: string; empty?: string }) {
  const w = max > 0 ? Math.round((n / max) * 100) : 0;
  return (
    <div className="grid grid-cols-[110px_1fr_34px] items-center gap-3 text-sm">
      <span className="text-slate-400">{label}</span>
      <div className="h-5 bg-slate-800/60 rounded relative overflow-hidden">
        {n > 0 ? (
          <b style={{ width: `${w}%` }} className={`block h-full rounded ${cls}`} />
        ) : (
          <span className="absolute inset-0 flex items-center pl-2 text-[11px] italic text-slate-500">
            {empty || "0"}
          </span>
        )}
      </div>
      <span className="text-right font-bold text-slate-200">{n}</span>
    </div>
  );
}

const pct = (n: number, d: number) => (d > 0 ? Math.round((n / d) * 100) : 0);

export default function Dashboard() {
  const [tab, setTab] = useState("universo");
  const [sessions, setSessions] = useState<any[]>([]);
  const [git, setGit] = useState<any[]>([]);
  const [adrs, setAdrs] = useState<any[]>([]);
  const [docs, setDocs] = useState<any[]>([]);
  const [tracker, setTracker] = useState<any | null>(null);
  const [historial, setHistorial] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<Record<number, boolean>>({});

  useEffect(() => {
    Promise.all([
      loadJson("/data/sessions.json"),
      loadJson("/data/git_activity.json"),
      loadJson("/data/adrs.json"),
      loadJson("/data/docs.json"),
      loadObj("/data/tracker.json"),
      loadJson("/data/historial.json"),
    ]).then(([s, g, a, d, t, h]) => {
      setSessions(s);
      setGit(g);
      setAdrs(a);
      setDocs(d);
      setTracker(t);
      setHistorial(h);
      setLoading(false);
    });
  }, []);

  const tabs = [
    { id: "universo", label: "Universo & Expansión" },
    { id: "proyecto", label: "Proyecto" },
    { id: "feed", label: "Sesiones" },
    { id: "adrs", label: "ADRs" },
    { id: "git", label: "Commits" },
    { id: "docs", label: "Documentos" },
    { id: "contrato", label: "Contrato de entrada" },
    { id: "versiones", label: "Versiones" },
  ];

  const r = tracker?.resumen || null;
  const renglones: any[] = tracker?.renglones || [];
  const avisos: string[] = tracker?.avisos || [];
  const expansionItems = renglones.filter((x) => x.alcance === "EXPANSION");
  const bugs = renglones.filter((x) => x.tipo === "BUG");
  const feats = renglones.filter((x) => x.tipo === "FEATURE");
  const motor = renglones.filter((x) => x.tipo === "MOTOR");
  const bugsAbiertos = bugs.filter((x) => !x.cubierto);
  const prioCount = (p: string) => bugsAbiertos.filter((x) => x.prioridad === p).length;
  const maxPrio = Math.max(1, ...["P0", "P1", "P2", "P3"].map(prioCount));
  const densidad = r && r.base > 0 ? (r.bugs_abiertos / r.base).toFixed(2) : null;

  const SinTracker = (
    <Empty>
      Sin datos del tracker. Corre el motor: <span className="font-mono text-xs">python3 docengine/generate.py</span>
      <br />
      <span className="text-xs">con DOCENGINE_TRACKER y DOCENGINE_LINEA_BASE definidos.</span>
    </Empty>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-xl font-semibold text-slate-100">Core-Doc-Engine</h1>
        <p className="text-sm text-slate-400 mt-1">
          Cada agente reporta lo que hizo. Aquí se contrasta contra Git.
        </p>
      </header>

      <nav className="border-b border-slate-800 px-6 flex gap-6 sticky top-0 bg-slate-950 z-10 overflow-x-auto">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`py-3 text-sm border-b-2 -mb-px transition whitespace-nowrap ${
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

        {/* ---------- UNIVERSO & EXPANSIÓN ---------- */}
        {!loading && tab === "universo" && (!r ? SinTracker : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              <Tile num={r.universo} lbl="Universo total" />
              <Tile num={r.base} lbl={`Alcance base · ${pct(r.base, r.universo)}%`} tone="base" />
              <Tile num={r.expansion} lbl={`Expansión · ${pct(r.expansion, r.universo)}%`} tone="exp" />
              <Tile num={r.bugs_abiertos} lbl="Bugs abiertos" tone="red" />
            </div>

            <Card title="1 · Distribución del universo — base vs expansión">
              <StackBar
                segs={[
                  { w: pct(r.base, r.universo), cls: "bg-blue-600", label: `BASE · ${r.base} · ${pct(r.base, r.universo)}%` },
                  { w: pct(r.expansion, r.universo), cls: "bg-cyan-600", label: `EXPANSIÓN · ${r.expansion}` },
                ]}
              />
              {r.sin_alcance_determinable > 0 && (
                <p className="text-xs text-amber-400 mt-2">
                  {r.sin_alcance_determinable} renglón(es) sin alcance determinable — revisa los avisos.
                </p>
              )}
              {expansionItems.length > 0 && (
                <div className="mt-3 pt-3 border-t border-dashed border-slate-700">
                  <div className="text-xs text-slate-400 mb-2">
                    <strong className="text-slate-300">Los {expansionItems.length} de expansión</strong> — entraron después de la línea base ({tracker.linea_base || "[FALTA]"}):
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {expansionItems.map((x) => (
                      <span key={x.id} className="text-[11px] font-semibold bg-cyan-950/60 text-cyan-300 border border-cyan-800 rounded-full px-2.5 py-0.5">
                        {x.id} {String(x.descripcion || "").slice(0, 34)}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-slate-400 mt-2">
                    El alcance creció <strong className="text-slate-200">{pct(r.expansion, r.base)}%</strong> sobre la base ({r.base} → {r.universo}). Verificados de esos {r.expansion}: <strong className="text-slate-200">{expansionItems.filter((x) => x.cubierto).length}</strong>.
                  </div>
                </div>
              )}
            </Card>

            <Card title="2 · Densidad de errores sobre el universo">
              <div className="space-y-2">
                <BarRow label="Total abiertos" n={r.bugs_abiertos} max={Math.max(1, r.bugs_abiertos)} cls="bg-red-600" />
                <BarRow label="▪ Core / Sistema" n={r.bugs_core} max={Math.max(1, r.bugs_abiertos)} cls="bg-red-600" />
                <BarRow
                  label="▪ De expansión"
                  n={r.bugs_expansion}
                  max={Math.max(1, r.bugs_abiertos)}
                  cls="bg-orange-500"
                  empty="sin superficie todavía — nada de expansión está construido"
                />
              </div>
              {densidad && (
                <p className="text-xs text-slate-400 mt-3 pt-3 border-t border-dashed border-slate-700">
                  <strong className="text-slate-200">Densidad actual:</strong> {r.bugs_abiertos} bugs sobre {r.base} ítems base = <strong className="text-slate-200">{densidad} bugs por ítem</strong>. El carril de expansión se llena solo conforme la expansión se construya — hoy un número ahí sería inventado.
                </p>
              )}
            </Card>

            <Card title="3 · Cobertura verificada en vivo">
              <div className="h-8 rounded-lg border border-slate-800 bg-emerald-950/30 relative overflow-hidden">
                {r.cobertura_pct > 0 && (
                  <b style={{ width: `${r.cobertura_pct}%` }} className="block h-full bg-emerald-600/70" />
                )}
                <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-emerald-300">
                  {r.cobertura_pct}% · {r.verificados_en_vivo} de {r.universo} verificados
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-2">
                Sube solo con registro firmado en <span className="font-mono">verificaciones/</span> — nunca al “subir código”.
              </p>
            </Card>

            {avisos.length > 0 && (
              <Card title={`Avisos del motor · ${avisos.length}`}>
                <ul className="space-y-1.5">
                  {avisos.map((a, i) => (
                    <li key={i} className="text-xs font-mono text-amber-300/90 break-all">{a}</li>
                  ))}
                </ul>
              </Card>
            )}

            <Card title="Lectura para la negociación">
              <ul className="text-sm text-slate-300 space-y-2 list-disc pl-5">
                <li>Se pidió <strong>{pct(r.expansion, r.base)}% más de alcance</strong> después de fijar la línea base ({r.base} → {r.universo} ítems).</li>
                <li><strong>{expansionItems.filter((x) => x.cubierto).length} de {r.expansion}</strong> ítems de expansión verificados. No hay deuda oculta: está declarada.</li>
                <li><strong>{r.bugs_abiertos} incidencias</strong> siguen abiertas, {prioCount("P0")} de ellas P0.</li>
                <li>La regla que sostiene todo: <strong>ningún número de este tablero se teclea.</strong> Si no está en Git o en un registro firmado, no aparece.</li>
              </ul>
            </Card>
          </>
        ))}

        {/* ---------- PROYECTO ---------- */}
        {!loading && tab === "proyecto" && (!r ? SinTracker : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              <Tile num={r.universo} lbl="Alcance total" />
              <Tile num={<>{r.verificados_en_vivo}<span className="text-sm text-slate-500"> / {r.universo}</span></>} lbl={`Cubierto · ${r.cobertura_pct}%`} />
              <Tile num={r.bugs_abiertos} lbl="Bugs abiertos" tone="red" />
              <Tile num={prioCount("P0")} lbl="P0 críticos" tone="red" />
            </div>

            <Card title={`Alcance por tipo — ${r.universo} ítems`}>
              <StackBar
                segs={[
                  { w: pct(bugs.length, r.universo), cls: "bg-blue-700", label: `Bugs · ${bugs.length}` },
                  { w: pct(feats.length, r.universo), cls: "bg-blue-500", label: `Features · ${feats.length}` },
                  { w: pct(motor.length, r.universo), cls: "bg-slate-500", label: `Motor · ${motor.length}` },
                ]}
              />
            </Card>

            <Card title="Bugs abiertos por prioridad">
              <div className="space-y-2">
                {["P0", "P1", "P2", "P3"].map((p) => (
                  <BarRow key={p} label={p} n={prioCount(p)} max={maxPrio} cls={p === "P0" ? "bg-red-700" : p === "P1" ? "bg-orange-600" : p === "P2" ? "bg-amber-500" : "bg-yellow-600/60"} />
                ))}
              </div>
            </Card>

            <Card title="Features solicitados">
              {feats.length === 0 && <p className="text-sm text-slate-600">Ninguno en el tracker.</p>}
              <ul className="divide-y divide-slate-800">
                {feats.map((f) => (
                  <li key={f.id} className="py-2 flex items-start gap-2.5 text-sm">
                    <span className={`flex-none text-[10px] font-bold uppercase rounded-full border px-2 py-0.5 ${f.alcance === "EXPANSION" ? "bg-cyan-950/60 text-cyan-300 border-cyan-800" : "bg-blue-950/60 text-blue-300 border-blue-800"}`}>
                      {f.id} · {f.alcance === "EXPANSION" ? "expansión" : f.alcance === "BASE" ? "base" : "?"}
                    </span>
                    <span className="text-slate-300">{f.descripcion}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card title="Motor (Core-Doc-Engine)">
              <ul className="divide-y divide-slate-800">
                {motor.map((m) => (
                  <li key={m.id} className="py-2 flex items-start gap-2.5 text-sm">
                    <span className={`flex-none text-[10px] font-bold uppercase rounded-full border px-2 py-0.5 ${m.alcance === "EXPANSION" ? "bg-cyan-950/60 text-cyan-300 border-cyan-800" : "bg-slate-800 text-slate-300 border-slate-600"}`}>
                      {m.id}
                    </span>
                    <span className="text-slate-300">{m.descripcion}</span>
                  </li>
                ))}
              </ul>
            </Card>

            <Card title="Bugs — backlog">
              <ul className="divide-y divide-slate-800">
                {bugs.map((b) => (
                  <li key={b.id} className="py-2 flex items-start gap-2.5 text-sm">
                    <span className={`flex-none text-[10px] font-bold uppercase rounded-full border px-2 py-0.5 ${PRIO_CLS[b.prioridad] || PRIO_CLS.P3}`}>
                      {b.prioridad} · {b.id}
                    </span>
                    <span className={b.cubierto ? "text-slate-500 line-through" : "text-slate-300"}>{b.descripcion}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </>
        ))}

        {/* ---------- SESIONES (existente, sin cambios) ---------- */}
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

        {/* ---------- ADRs (existente, sin cambios) ---------- */}
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

        {/* ---------- COMMITS (existente, sin cambios) ---------- */}
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

        {/* ---------- DOCS (existente, sin cambios) ---------- */}
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

        {/* ---------- CONTRATO DE ENTRADA (estático — es la regla, no datos) ---------- */}
        {!loading && tab === "contrato" && (
          <>
            <div className="border border-amber-900/50 bg-amber-950/30 text-amber-300/90 rounded-lg px-4 py-2.5 text-xs mb-4">
              Esto es lo que hace que las gráficas se llenen solas. Sin este contrato, todo número es tecleado — y por lo tanto, opinable.
            </div>

            <Card title="Esquema del ítem (fuente: tracker markdown)">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-slate-500 uppercase tracking-wide">
                    <th className="py-1.5 pr-3">Campo</th><th className="py-1.5 pr-3">Valores</th><th className="py-1.5">Cómo se determina</th>
                  </tr>
                </thead>
                <tbody className="text-slate-300">
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">id</td><td className="pr-3 font-mono">B-nn · F-nn · DE-nn</td><td>Asignado al entrar. Inmutable.</td></tr>
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">tipo</td><td className="pr-3 font-mono">BUG · FEATURE · MOTOR</td><td>Se deriva del prefijo del id.</td></tr>
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">alcance</td><td className="pr-3 font-mono">BASE · EXPANSION</td><td><strong>Derivado</strong>: fecha_intake &gt; línea base → EXPANSION. No se teclea.</td></tr>
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">origen</td><td className="pr-3 font-mono">CORE · F-nn</td><td>Solo para BUG. El motor exige que ese F-nn exista.</td></tr>
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">prioridad</td><td className="pr-3 font-mono">P0 – P3</td><td>Capturada. Si falta → [FALTA CLASIFICAR].</td></tr>
                  <tr className="border-t border-slate-800"><td className="py-1.5 pr-3 font-mono">fecha_intake</td><td className="pr-3 font-mono">ISO</td><td>La pone Git (primer commit que menciona el ID). Marcador [intake:] solo vale en el commit inicial; fuera de ahí se denuncia y se ignora.</td></tr>
                </tbody>
              </table>
              <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-dashed border-slate-700">
                <strong className="text-slate-400">La clave anti-manipulación:</strong> alcance no es un campo que alguien palomea. Un feature no puede “volverse base” porque a alguien le convenga.
              </p>
            </Card>

            <Card title="Contrato del commit">
              <pre className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 overflow-auto">{`fix(avisos): corregir cálculo de vigencia del aviso preventivo

La resta usaba fecha de captura en vez de fecha de aviso.

Ref: B-05
ADR: 037`}</pre>
              <p className="text-xs text-slate-500 mt-2">
                Rama: <span className="font-mono">fix/B-05-vigencia-aviso</span> · el ID nace ANTES de la rama · varios ítems: <span className="font-mono">Ref: B-07, B-08</span>
              </p>
            </Card>

            <Card title="Contrato de la verificación (lo que Git no puede probar)">
              <pre className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs font-mono text-slate-300 overflow-auto">{`verificaciones/2026-07-30.jsonl

{"id":"B-05","verifico":"Leo","fecha":"2026-07-30",
 "entorno":"N901","evidencia":"vigencia muestra 30 días en aviso 1842",
 "resultado":"ok"}`}</pre>
              <p className="text-xs text-slate-500 mt-2">
                Append-only. <strong className="text-slate-400">No lo escribe quien programó</strong> — un agente no se autocertifica. Un <span className="font-mono">"resultado":"falla"</span> también se registra: el intento fallido es evidencia.
              </p>
            </Card>
          </>
        )}

        {/* ---------- VERSIONES ---------- */}
        {!loading && tab === "versiones" && (!tracker ? SinTracker : (
          <>
            <div className="border border-amber-900/50 bg-amber-950/30 text-amber-300/90 rounded-lg px-4 py-2.5 text-xs mb-4">
              Dos cosas distintas se versionan: <strong>el motor</strong> (el software) y <strong>los datos</strong> (el estado del proyecto en una fecha).
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              <Tile num={`v${tracker.motor || "?"}`} lbl="Motor · SemVer" tone="base" />
              <Tile num={<span className="font-mono text-lg">{tracker.commit_datos || "[FALTA COMMIT]"}</span>} lbl="Datos · commit" />
              <Tile num={<span className="text-lg">{fmt(tracker.generado)}</span>} lbl="Fecha del build" />
              <Tile num={historial.length} lbl="Builds registrados" />
            </div>

            <Card title="Historial de builds">
              {historial.length === 0 && <p className="text-sm text-slate-600">Sin corridas registradas en historial.jsonl.</p>}
              {historial.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-left text-slate-500 uppercase tracking-wide">
                        <th className="py-1.5 pr-3">Build</th><th className="pr-3">Motor</th><th className="pr-3">Commit</th>
                        <th className="pr-3">Universo</th><th className="pr-3">Δ</th>
                        <th className="pr-3">Bugs</th><th className="pr-3">Δ</th>
                        <th className="pr-3">Cubierto</th><th>Δ</th>
                      </tr>
                    </thead>
                    <tbody className="text-slate-300">
                      {[...historial].reverse().map((h, i, arr) => {
                        const prev = arr[i + 1];
                        const delta = (a?: number, b?: number) =>
                          prev == null || a == null || b == null ? "—" : a - b === 0 ? "0" : a - b > 0 ? `+${a - b}` : `${a - b}`;
                        const dcls = (a?: number, b?: number, goodDown?: boolean) => {
                          if (prev == null || a == null || b == null || a === b) return "text-slate-500";
                          const up = a > b;
                          return (goodDown ? !up : up) ? "text-emerald-400" : "text-orange-400";
                        };
                        const bugsN = (h.bugs_core ?? 0) + (h.bugs_exp ?? 0);
                        const bugsP = prev ? (prev.bugs_core ?? 0) + (prev.bugs_exp ?? 0) : undefined;
                        return (
                          <tr key={i} className="border-t border-slate-800">
                            <td className="py-1.5 pr-3">{h.build}</td>
                            <td className="pr-3">{h.motor}</td>
                            <td className="pr-3 font-mono">{h.commit}</td>
                            <td className="pr-3 font-bold">{h.universo}</td>
                            <td className={`pr-3 ${dcls(h.universo, prev?.universo, true)}`}>{delta(h.universo, prev?.universo)}</td>
                            <td className="pr-3 font-bold">{bugsN}</td>
                            <td className={`pr-3 ${dcls(bugsN, bugsP, true)}`}>{delta(bugsN, bugsP)}</td>
                            <td className="pr-3 font-bold">{h.cubierto}</td>
                            <td className={dcls(h.cubierto, prev?.cubierto)}>{delta(h.cubierto, prev?.cubierto)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
              <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-dashed border-slate-700">
                No duplica a Git: es un caché de datos derivados, reconstruible. Regresar N versiones = <span className="font-mono">git checkout &lt;hash&gt; -- tracker</span> y volver a generar. Sin base de datos, sin backend.
              </p>
            </Card>
          </>
        ))}
      </main>

      <footer className="border-t border-slate-800 px-6 py-4 text-center text-xs text-slate-600">
        docengine <strong className="text-slate-400">v{tracker?.motor || "?"}</strong> · datos{" "}
        <span className="font-mono">{tracker?.commit_datos || "[FALTA COMMIT]"}</span> · build {fmt(tracker?.generado)} · fuente de verdad: Git, no esta pintura.
      </footer>
    </div>
  );
}
