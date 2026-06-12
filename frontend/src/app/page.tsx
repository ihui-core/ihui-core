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
          </>
        )}
      </div>
    </div>
  );
}
