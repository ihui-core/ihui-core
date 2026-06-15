'use client';

import { useEffect, useMemo, useState } from 'react';

type Caso = {
  id: number;
  titulo: string;
  descripcion?: string | null;
  estado: string;
};

type Evento = {
  id: number;
  tipo_evento: string;
  descripcion: string;
  created_at?: string | null;
  usuario_nombre?: string | null;
};

type Usuario = {
  id: number;
  nombre: string;
  email: string;
  activo: boolean;
};

type Tarea = {
  id: number;
  titulo: string;
  descripcion?: string | null;
  nodo_titulo?: string | null;
  nodo_tipo?: string | null;
  prioridad: string;
  estado: string;
  fecha_vencimiento?: string | null;
  asignado_por?: string | null;
};

type Incidente = {
  id: number;
  title: string;
  prioridad?: string | null;
  status?: string | null;
  app_source?: string | null;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002';

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`No se pudo cargar ${path}`);
  return response.json() as Promise<T>;
}

function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub: string;
  accent?: string;
}) {
  return (
    <div style={{
      backgroundColor: '#1A1A1A',
      border: '1px solid #2A2A2A',
      borderRadius: '12px',
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    }}>
      <span style={{
        fontSize: '11px',
        color: '#9CA3AF',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
      }}>
        {label}
      </span>
      <span style={{
        fontSize: '3rem',
        fontWeight: 700,
        color: accent || '#F9FAFB',
        fontFamily: "'DM Serif Display', Georgia, serif",
        lineHeight: 1,
      }}>
        {value}
      </span>
      <span style={{ fontSize: '12px', color: '#6B7280' }}>{sub}</span>
    </div>
  );
}

export default function Home() {
  const [casos, setCasos] = useState<Caso[]>([]);
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<{nombre: string; rol: string} | null>(null);
  const [incidentes, setIncidentes] = useState<Incidente[]>([]);
  const [misTareas, setMisTareas] = useState<Tarea[]>([]);
  const [tabTareas, setTabTareas] = useState<'pendientes' | 'finalizadas'>('pendientes');
  const [filtroPrioridad, setFiltroPrioridad] = useState<string>('TODAS');
  const [modalAbierto, setModalAbierto] = useState(false);
  const [formTitulo, setFormTitulo] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formPrioridad, setFormPrioridad] = useState('MEDIA');
  const [enviando, setEnviando] = useState(false);

  const [modalAsignarAbierto, setModalAsignarAbierto] = useState(false);
  const [asignarTitulo, setAsignarTitulo] = useState('');
  const [asignarDesc, setAsignarDesc] = useState('');
  const [asignarResponsable, setAsignarResponsable] = useState('');
  const [asignarNodoTitulo, setAsignarNodoTitulo] = useState('');
  const [asignarPrioridad, setAsignarPrioridad] = useState('MEDIA');
  const [asignarFechaVenc, setAsignarFechaVenc] = useState('');
  const [enviandoAsignar, setEnviandoAsignar] = useState(false);
  const [tareaExpandida, setTareaExpandida] = useState<number | null>(null);

  const puedeAsignar = usuario && ['superadmin', 'notario', 'cfo', 'coordinador', 'abogado'].includes(usuario.rol);

  const recargarTareas = async () => {
    const res = await fetch(`${apiBaseUrl}/tareas/mis-tareas?incluir_completadas=true`, { credentials: 'include', cache: 'no-store' });
    if (res.ok) setMisTareas(await res.json());
  };

  const recargarIncidentes = async () => {
    const res = await fetch(`${apiBaseUrl}/incidentes`, { credentials: 'include', cache: 'no-store' });
    if (res.ok) setIncidentes(await res.json());
  };

  const handleAsignar = async () => {
    if (!asignarTitulo.trim() || !asignarResponsable) return;
    setEnviandoAsignar(true);
    try {
      await fetch(`${apiBaseUrl}/tareas/asignar`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titulo: asignarTitulo,
          descripcion: asignarDesc || null,
          responsable_ref: asignarResponsable,
          nodo_titulo: asignarNodoTitulo || null,
          nodo_tipo: 'TAREA',
          prioridad: asignarPrioridad,
          fecha_vencimiento: asignarFechaVenc || null,
        }),
      });
      setModalAsignarAbierto(false);
      setAsignarTitulo('');
      setAsignarDesc('');
      setAsignarResponsable('');
      setAsignarNodoTitulo('');
      setAsignarPrioridad('MEDIA');
      setAsignarFechaVenc('');
      await recargarTareas();
    } finally {
      setEnviandoAsignar(false);
    }
  };

  const handleEnviar = async () => {
    if (!formTitulo.trim()) return;
    setEnviando(true);
    try {
      await fetch(`${apiBaseUrl}/incidentes`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titulo: formTitulo,
          descripcion: formDesc,
          app_source: 'ihui-core',
          tipo: 'BUG',
          prioridad: formPrioridad,
        }),
      });
      setModalAbierto(false);
      setFormTitulo('');
      setFormDesc('');
      setFormPrioridad('MEDIA');
      await recargarIncidentes();
    } finally {
      setEnviando(false);
    }
  };

  useEffect(() => {
    let active = true;
    async function loadDashboard() {
      try {
        const meRes = await fetch(`${apiBaseUrl}/auth/me`, { credentials: 'include', cache: 'no-store' });
        if (!meRes.ok) {
          window.location.href = '/login';
          return;
        }
        const meData = await meRes.json();
        if (active) setUsuario(meData);

        const [casosResponse, eventosResponse, usuariosResponse] = await Promise.all([
          fetchJson<Caso[]>('/casos/'),
          fetchJson<Evento[]>('/eventos'),
          fetchJson<Usuario[]>('/usuarios'),
        ]);
        if (!active) return;
        setCasos(casosResponse);
        setEventos(eventosResponse);
        setUsuarios(usuariosResponse);
        const incRes = await fetch(`${apiBaseUrl}/incidentes`, { credentials: 'include', cache: 'no-store' });
        if (incRes.ok && active) setIncidentes(await incRes.json());
        const tareasRes = await fetch(`${apiBaseUrl}/tareas/mis-tareas?incluir_completadas=true`, { credentials: 'include', cache: 'no-store' });
        if (tareasRes.ok && active) setMisTareas(await tareasRes.json());
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'No se pudo conectar con la API');
      } finally {
        if (active) setLoading(false);
      }
    }
    loadDashboard();
    return () => { active = false; };
  }, []);

  const casosAbiertos = useMemo(() =>
    casos.filter(c => ['ABIERTO', 'EN_PROCESO', 'PENDIENTE'].includes(c.estado?.toUpperCase())).length,
    [casos]
  );

  const ultimosEventos = useMemo(() =>
    [...eventos].slice(-5).reverse(),
    [eventos]
  );

  const mes = new Date().toLocaleString('es-MX', { month: 'long', year: 'numeric' });

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#141414',
      padding: '2rem',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              color: '#F9FAFB',
              fontFamily: "'DM Serif Display', Georgia, serif",
              fontStyle: 'italic',
              margin: 0,
            }}>
              ihui CORE
            </h1>
            <button
              onClick={async () => {
                await fetch(`${apiBaseUrl}/auth/logout`, { method: 'POST', credentials: 'include' }).catch(() => {});
                sessionStorage.clear();
                window.location.href = '/login';
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = '#EF4444'; e.currentTarget.style.borderColor = '#EF4444'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = '#6B7280'; e.currentTarget.style.borderColor = '#2A2A2A'; }}
              style={{
                background: 'none',
                border: '1px solid #2A2A2A',
                borderRadius: '8px',
                color: '#6B7280',
                fontSize: '13px',
                cursor: 'pointer',
                fontFamily: "'DM Sans', sans-serif",
                padding: '0.5rem 1rem',
                transition: 'color 0.15s, border-color 0.15s',
              }}
            >
              Cerrar sesión
            </button>
          </div>
          <p style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>
            Gobernabilidad institucional · {mes}
          </p>
          {usuario && (
            <p style={{ fontSize: '13px', color: '#2A7A5A', marginTop: '2px' }}>
              {usuario.nombre} · {usuario.rol}
            </p>
          )}
        </div>

        {/* Buscador */}
        <input
          style={{
            width: '100%',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            backgroundColor: '#1A1A1A',
            border: '1px solid #2A2A2A',
            color: '#F9FAFB',
            fontSize: '13px',
            marginBottom: '2.5rem',
            outline: 'none',
            boxSizing: 'border-box',
          }}
          placeholder="Buscar personas, casos, tareas o actividad..."
        />

        {/* Loading */}
        {loading && (
          <p style={{ color: '#6B7280', fontSize: '13px' }}>Cargando…</p>
        )}

        {/* Error */}
        {error && (
          <div style={{
            color: '#EF4444',
            fontSize: '13px',
            backgroundColor: '#1A0000',
            border: '1px solid #3A0000',
            borderRadius: '8px',
            padding: '0.75rem 1rem',
            marginBottom: '1.5rem',
          }}>
            {error}
          </div>
        )}

        {/* Stats */}
        {!loading && !error && (
          <>
            {/* Mis tareas */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <p style={{
                fontSize: '11px', color: '#4B5563', textTransform: 'uppercase',
                letterSpacing: '0.08em', margin: 0,
              }}>
                Mis tareas
              </p>
              {puedeAsignar && (
                <button
                  onClick={() => setModalAsignarAbierto(true)}
                  style={{
                    background: 'none',
                    border: '1px solid #2A7A5A',
                    borderRadius: '6px',
                    color: '#2A7A5A',
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '3px 10px',
                    cursor: 'pointer',
                    fontFamily: "'DM Sans', sans-serif",
                    transition: 'background 0.15s, color 0.15s',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#2A7A5A'; e.currentTarget.style.color = '#fff'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; e.currentTarget.style.color = '#2A7A5A'; }}
                >
                  + Asignar tarea
                </button>
              )}
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', borderBottom: '1px solid #2A2A2A', marginBottom: '1rem' }}>
              {(['pendientes', 'finalizadas'] as const).map((tab) => (
                <button key={tab} onClick={() => setTabTareas(tab)} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  padding: '0.5rem 1rem', fontSize: '13px',
                  color: tabTareas === tab ? '#2A7A5A' : '#6B7280',
                  borderBottom: tabTareas === tab ? '2px solid #2A7A5A' : '2px solid transparent',
                  marginBottom: '-1px', fontFamily: "'DM Sans', sans-serif",
                  textTransform: 'capitalize', transition: 'color 0.15s',
                }}>
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            <div style={{
              backgroundColor: '#1A1A1A', border: '1px solid #2A2A2A',
              borderRadius: '12px', padding: '1.5rem', marginBottom: '2.5rem',
            }}>
              {(() => {
                const ESTADOS_TAREA: Record<string, { label: string; color: string }> = {
                  PENDING:     { label: 'Pendiente',  color: '#6B7280' },
                  IN_PROGRESS: { label: 'En proceso', color: '#C8920A' },
                  BLOCKED:     { label: 'Bloqueada',  color: '#B84A1E' },
                  DONE:        { label: 'Completada', color: '#2A7A5A' },
                  CANCELLED:   { label: 'Cancelada',  color: '#4B5563' },
                };
                const PRIORIDAD_ORDER: Record<string, number> = { CRITICA: 0, ALTA: 1, MEDIA: 2, BAJA: 3 };
                const PRIORIDAD_COLOR: Record<string, string> = {
                  CRITICA: '#EF4444', ALTA: '#C8920A', MEDIA: '#6B7280', BAJA: '#4B5563',
                };
                const visibles = misTareas
                  .filter(t => tabTareas === 'pendientes'
                    ? t.estado !== 'DONE' && t.estado !== 'CANCELLED'
                    : t.estado === 'DONE' || t.estado === 'CANCELLED')
                  .sort((a, b) => (PRIORIDAD_ORDER[a.prioridad?.toUpperCase()] ?? 9) - (PRIORIDAD_ORDER[b.prioridad?.toUpperCase()] ?? 9));
                const esFinalizada = tabTareas === 'finalizadas';
                return visibles.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                    {visibles.map((t) => {
                      const colorP = PRIORIDAD_COLOR[t.prioridad?.toUpperCase()] ?? '#6B7280';
                      const expandida = tareaExpandida === t.id;
                      const fechaFmt = t.fecha_vencimiento
                        ? new Date(t.fecha_vencimiento).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })
                        : 'Sin fecha límite';
                      const estadoInfo = ESTADOS_TAREA[t.estado] ?? { label: t.estado, color: '#6B7280' };
                      const tituloApagado = t.estado === 'DONE' || t.estado === 'CANCELLED';
                      return (
                        <div key={t.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                          <select
                            value={t.estado}
                            onClick={(e) => e.stopPropagation()}
                            onChange={async (e) => {
                              const nuevoEstado = e.target.value;
                              const res = await fetch(`${apiBaseUrl}/tareas/${t.id}/estado`, {
                                method: 'PATCH',
                                credentials: 'include',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ estado: nuevoEstado }),
                              });
                              if (res.ok) {
                                await recargarTareas();
                              } else if (res.status === 403) {
                                const data = await res.json();
                                alert(data.detail ?? 'No tienes permiso para este cambio');
                              }
                            }}
                            style={{
                              appearance: 'none',
                              WebkitAppearance: 'none',
                              background: '#0D0D0D',
                              border: `1.5px solid ${estadoInfo.color}`,
                              borderRadius: '6px',
                              color: estadoInfo.color,
                              fontSize: '10px',
                              fontWeight: 600,
                              padding: '3px 6px',
                              cursor: 'pointer',
                              flexShrink: 0,
                              marginTop: '1px',
                              fontFamily: "'DM Sans', sans-serif",
                              outline: 'none',
                              minWidth: '88px',
                            }}
                          >
                            <option value="PENDING">Pendiente</option>
                            <option value="IN_PROGRESS">En proceso</option>
                            <option value="BLOCKED">Bloqueada</option>
                            <option value="DONE">Completada</option>
                            {puedeAsignar && <option value="CANCELLED">Cancelada</option>}
                          </select>
                          <div
                            onClick={() => setTareaExpandida(expandida ? null : t.id)}
                            style={{ cursor: 'pointer', flex: 1, minWidth: 0 }}
                          >
                            <p style={{ fontSize: '13px', color: tituloApagado ? '#4B5563' : '#F9FAFB', margin: 0, fontWeight: 500, textDecoration: tituloApagado ? 'line-through' : 'none' }}>
                              {t.titulo}
                            </p>
                            <p style={{ fontSize: '11px', color: '#6B7280', margin: '2px 0 0' }}>
                              {[t.nodo_titulo, t.nodo_tipo].filter(Boolean).join(' · ')}
                              {(t.nodo_titulo || t.nodo_tipo) && ' · '}
                              <span style={{ color: colorP, fontWeight: 600 }}>{t.prioridad}</span>
                            </p>
                            {expandida && (
                              <div style={{
                                marginTop: '0.625rem',
                                padding: '0.625rem 0.75rem',
                                backgroundColor: '#141414',
                                borderRadius: '8px',
                                border: '1px solid #2A2A2A',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '4px',
                              }}>
                                <p style={{ fontSize: '12px', color: '#9CA3AF', margin: 0 }}>
                                  {t.descripcion || 'Sin descripción'}
                                </p>
                                <p style={{ fontSize: '11px', color: '#6B7280', margin: 0 }}>
                                  Vence: {fechaFmt}
                                </p>
                                {t.asignado_por && (
                                  <p style={{ fontSize: '11px', color: '#6B7280', margin: 0 }}>
                                    Asignada por: {t.asignado_por}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p style={{ fontSize: '13px', color: '#6B7280', margin: 0 }}>
                    {esFinalizada ? 'Sin tareas finalizadas.' : 'Sin tareas pendientes.'}
                  </p>
                );
              })()}
            </div>

            <p style={{
              fontSize: '11px',
              color: '#4B5563',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: '0.75rem',
            }}>
              Indicadores
            </p>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
              gap: '1rem',
              marginBottom: '2.5rem',
            }}>
              <StatCard
                label="Casos abiertos"
                value={casosAbiertos}
                sub={`De ${casos.length} casos totales`}
                accent={casosAbiertos > 0 ? '#C8920A' : undefined}
              />
              <StatCard
                label="Usuarios registrados"
                value={usuarios.length}
                sub="Cuentas activas en el sistema"
                accent={usuarios.length > 0 ? '#2A7A5A' : undefined}
              />
              <StatCard
                label="Eventos registrados"
                value={eventos.length}
                sub="Actividad institucional total"
              />
            </div>

            {/* Actividad reciente */}
            <p style={{
              fontSize: '11px',
              color: '#4B5563',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: '0.75rem',
            }}>
              Actividad reciente
            </p>
            <div style={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '12px',
              padding: '1.5rem',
            }}>
              {ultimosEventos.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {ultimosEventos.map((evento) => (
                    <div key={evento.id} style={{
                      borderBottom: '1px solid #2A2A2A',
                      paddingBottom: '1rem',
                    }}>
                      <p style={{ fontSize: '13px', color: '#F9FAFB', margin: 0, fontWeight: 500 }}>
                        {evento.tipo_evento}
                      </p>
                      <p style={{ fontSize: '12px', color: '#6B7280', margin: '4px 0 0' }}>
                        {evento.descripcion}
                      </p>
                      {evento.usuario_nombre && (
                        <p style={{ fontSize: '11px', color: '#4B5563', margin: '4px 0 0' }}>
                          por {evento.usuario_nombre}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ fontSize: '13px', color: '#6B7280', margin: 0 }}>
                  Sin actividad reciente.
                </p>
              )}
            </div>

            {/* Incidentes */}
            <p style={{
              fontSize: '11px',
              color: '#4B5563',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              marginBottom: '0.75rem',
              marginTop: '2.5rem',
            }}>
              Incidentes
            </p>
            {/* Filtros de prioridad */}
            <div style={{ display: 'flex', gap: '6px', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
              {['TODAS', 'CRITICA', 'ALTA', 'MEDIA', 'BAJA'].map((p) => (
                <button
                  key={p}
                  onClick={() => setFiltroPrioridad(p)}
                  style={{
                    padding: '3px 10px',
                    fontSize: '11px',
                    fontWeight: 500,
                    borderRadius: '6px',
                    border: `1px solid ${filtroPrioridad === p ? '#2A7A5A' : '#2A2A2A'}`,
                    backgroundColor: filtroPrioridad === p ? '#2A7A5A' : '#1A1A1A',
                    color: filtroPrioridad === p ? '#fff' : '#6B7280',
                    cursor: 'pointer',
                    fontFamily: "'DM Sans', sans-serif",
                    transition: 'background 0.15s, color 0.15s',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>

            <div style={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '12px',
              padding: '1.5rem',
            }}>
              {(() => {
                const visibles = filtroPrioridad === 'TODAS'
                  ? incidentes
                  : incidentes.filter(i => (i.status ?? '').toUpperCase() === filtroPrioridad);
                return visibles.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {visibles.map((inc) => {
                    const PRIORIDAD_COLOR: Record<string, string> = {
                      CRITICA: '#EF4444',
                      ALTA:    '#C8920A',
                      MEDIA:   '#6B7280',
                      BAJA:    '#4B5563',
                    };
                    const color = PRIORIDAD_COLOR[(inc.status ?? inc.prioridad ?? '').toUpperCase()] ?? '#6B7280';
                    return (
                      <div key={inc.id} style={{
                        borderBottom: '1px solid #2A2A2A',
                        paddingBottom: '1rem',
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'space-between',
                        gap: '1rem',
                      }}>
                        <div>
                          <p style={{ fontSize: '13px', color: '#F9FAFB', margin: 0, fontWeight: 500 }}>
                            {inc.title}
                          </p>
                          <p style={{ fontSize: '12px', margin: '4px 0 0' }}>
                            <span style={{ color, fontWeight: 600 }}>{inc.status ?? inc.prioridad}</span>
                            {inc.app_source && (
                              <span style={{ color: '#4B5563' }}> · {inc.app_source}</span>
                            )}
                          </p>
                        </div>
                        <button
                          onClick={async () => {
                            await fetch(`${apiBaseUrl}/incidentes/${inc.id}/resolver`, {
                              method: 'PATCH',
                              credentials: 'include',
                            });
                            await recargarIncidentes();
                          }}
                          style={{
                            padding: '4px 12px',
                            fontSize: '11px',
                            fontWeight: 500,
                            backgroundColor: '#2A2A2A',
                            color: '#9CA3AF',
                            border: '1px solid #3A3A3A',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            flexShrink: 0,
                          }}
                        >
                          Resolver
                        </button>
                      </div>
                    );
                  })}
                </div>
                ) : (
                <p style={{ fontSize: '13px', color: '#6B7280', margin: 0 }}>
                  {filtroPrioridad === 'TODAS' ? 'Sin incidentes activos.' : `Sin incidentes con prioridad ${filtroPrioridad}.`}
                </p>
                );
              })()}
            </div>
          </>
        )}
      </div>

      {/* Botón flotante */}
      <div style={{ position: 'fixed', bottom: '2rem', right: '2rem', zIndex: 50 }}>
        <div style={{ position: 'relative', display: 'inline-flex' }} className="group">
          <button
            onClick={() => setModalAbierto(true)}
            title="Reportar incidente"
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              color: '#6B7280',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
              transition: 'border-color 0.15s, color 0.15s',
              fontFamily: "'DM Sans', sans-serif",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#2A7A5A';
              e.currentTarget.style.color = '#2A7A5A';
              const tip = e.currentTarget.nextElementSibling as HTMLElement | null;
              if (tip) tip.style.opacity = '1';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#2A2A2A';
              e.currentTarget.style.color = '#6B7280';
              const tip = e.currentTarget.nextElementSibling as HTMLElement | null;
              if (tip) tip.style.opacity = '0';
            }}
          >
            ⚑
          </button>
          <span style={{
            position: 'absolute',
            bottom: '56px',
            right: 0,
            backgroundColor: '#2A2A2A',
            color: '#F9FAFB',
            fontSize: '11px',
            fontWeight: 500,
            padding: '4px 10px',
            borderRadius: '6px',
            whiteSpace: 'nowrap',
            opacity: 0,
            transition: 'opacity 0.15s',
            pointerEvents: 'none',
            fontFamily: "'DM Sans', sans-serif",
          }}>
            Reportar incidente
          </span>
        </div>
      </div>

      {/* Modal asignar tarea */}
      {modalAsignarAbierto && (
        <div
          onClick={() => setModalAsignarAbierto(false)}
          style={{
            position: 'fixed', inset: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 100,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '16px',
              padding: '2rem',
              width: '100%',
              maxWidth: '480px',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#F9FAFB' }}>
              Asignar tarea
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Título *</label>
              <input
                value={asignarTitulo}
                onChange={(e) => setAsignarTitulo(e.target.value)}
                placeholder="Título de la tarea"
                style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: '#F9FAFB', fontSize: '13px', outline: 'none' }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Descripción</label>
              <textarea
                value={asignarDesc}
                onChange={(e) => setAsignarDesc(e.target.value)}
                placeholder="Detalles opcionales..."
                rows={3}
                style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: '#F9FAFB', fontSize: '13px', outline: 'none', resize: 'vertical', fontFamily: "'DM Sans', sans-serif" }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Asignar a *</label>
              <select
                value={asignarResponsable}
                onChange={(e) => setAsignarResponsable(e.target.value)}
                style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: asignarResponsable ? '#F9FAFB' : '#6B7280', fontSize: '13px', outline: 'none' }}
              >
                <option value="">Seleccionar usuario...</option>
                {usuarios.map((u) => (
                  <option key={u.id} value={u.email}>{u.nombre} · {u.email}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Relacionado con</label>
              <input
                value={asignarNodoTitulo}
                onChange={(e) => setAsignarNodoTitulo(e.target.value)}
                placeholder="Caso, expediente, proyecto..."
                style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: '#F9FAFB', fontSize: '13px', outline: 'none' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Prioridad</label>
                <select
                  value={asignarPrioridad}
                  onChange={(e) => setAsignarPrioridad(e.target.value)}
                  style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: '#F9FAFB', fontSize: '13px', outline: 'none' }}
                >
                  <option value="BAJA">Baja</option>
                  <option value="MEDIA">Media</option>
                  <option value="ALTA">Alta</option>
                  <option value="CRITICA">Crítica</option>
                </select>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
                <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Fecha límite</label>
                <input
                  type="date"
                  value={asignarFechaVenc}
                  onChange={(e) => setAsignarFechaVenc(e.target.value)}
                  style={{ padding: '0.65rem 0.875rem', borderRadius: '8px', backgroundColor: '#0D0D0D', border: '1px solid #2A2A2A', color: '#F9FAFB', fontSize: '13px', outline: 'none', colorScheme: 'dark' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
              <button
                onClick={() => setModalAsignarAbierto(false)}
                style={{ padding: '0.6rem 1.25rem', backgroundColor: 'transparent', color: '#6B7280', border: '1px solid #2A2A2A', borderRadius: '8px', fontSize: '13px', cursor: 'pointer', fontFamily: "'DM Sans', sans-serif" }}
              >
                Cancelar
              </button>
              <button
                onClick={handleAsignar}
                disabled={enviandoAsignar || !asignarTitulo.trim() || !asignarResponsable}
                style={{
                  padding: '0.6rem 1.25rem',
                  backgroundColor: (enviandoAsignar || !asignarTitulo.trim() || !asignarResponsable) ? '#1A3A2A' : '#2A7A5A',
                  color: (enviandoAsignar || !asignarTitulo.trim() || !asignarResponsable) ? '#4B7A5A' : '#fff',
                  border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: 600,
                  cursor: (enviandoAsignar || !asignarTitulo.trim() || !asignarResponsable) ? 'not-allowed' : 'pointer',
                  transition: 'background 0.15s', fontFamily: "'DM Sans', sans-serif",
                }}
              >
                {enviandoAsignar ? 'Asignando…' : 'Asignar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      {modalAbierto && (
        <div
          onClick={() => setModalAbierto(false)}
          style={{
            position: 'fixed', inset: 0,
            backgroundColor: 'rgba(0,0,0,0.6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 100,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '16px',
              padding: '2rem',
              width: '100%',
              maxWidth: '440px',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#F9FAFB' }}>
              Reportar incidente
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Título</label>
              <input
                value={formTitulo}
                onChange={(e) => setFormTitulo(e.target.value)}
                placeholder="Descripción breve del incidente"
                style={{
                  padding: '0.65rem 0.875rem',
                  borderRadius: '8px',
                  backgroundColor: '#0D0D0D',
                  border: '1px solid #2A2A2A',
                  color: '#F9FAFB',
                  fontSize: '13px',
                  outline: 'none',
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Descripción</label>
              <textarea
                value={formDesc}
                onChange={(e) => setFormDesc(e.target.value)}
                placeholder="Detalles adicionales..."
                rows={3}
                style={{
                  padding: '0.65rem 0.875rem',
                  borderRadius: '8px',
                  backgroundColor: '#0D0D0D',
                  border: '1px solid #2A2A2A',
                  color: '#F9FAFB',
                  fontSize: '13px',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: "'DM Sans', sans-serif",
                }}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '11px', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Prioridad</label>
              <select
                value={formPrioridad}
                onChange={(e) => setFormPrioridad(e.target.value)}
                style={{
                  padding: '0.65rem 0.875rem',
                  borderRadius: '8px',
                  backgroundColor: '#0D0D0D',
                  border: '1px solid #2A2A2A',
                  color: '#F9FAFB',
                  fontSize: '13px',
                  outline: 'none',
                }}
              >
                <option value="BAJA">Baja</option>
                <option value="MEDIA">Media</option>
                <option value="ALTA">Alta</option>
                <option value="CRITICA">Crítica</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
              <button
                onClick={() => setModalAbierto(false)}
                style={{
                  padding: '0.6rem 1.25rem',
                  backgroundColor: 'transparent',
                  color: '#6B7280',
                  border: '1px solid #2A2A2A',
                  borderRadius: '8px',
                  fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                Cancelar
              </button>
              <button
                onClick={handleEnviar}
                disabled={enviando || !formTitulo.trim()}
                style={{
                  padding: '0.6rem 1.25rem',
                  backgroundColor: enviando || !formTitulo.trim() ? '#1A3A2A' : '#2A7A5A',
                  color: enviando || !formTitulo.trim() ? '#4B7A5A' : '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: enviando || !formTitulo.trim() ? 'not-allowed' : 'pointer',
                  transition: 'background 0.15s',
                }}
              >
                {enviando ? 'Enviando…' : 'Enviar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
