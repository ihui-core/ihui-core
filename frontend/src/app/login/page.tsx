'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
        credentials: 'include', // httpOnly cookie
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Credenciales inválidas');
      // Solo guardamos datos no sensibles — el token nunca toca JS
      sessionStorage.setItem('usuario', JSON.stringify(data.usuario));
      window.location.href = '/';
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#141414',
      display: 'flex',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      {/* Panel izquierdo */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem',
        borderRight: '1px solid #2A2A2A',
      }}>
        <Image src="/bird.svg" alt="ihui" width={64} height={64} style={{ marginBottom: '1.5rem' }} />
        <h1 style={{
          fontSize: '100px',
          fontFamily: "'DM Serif Display', Georgia, serif",
          fontStyle: 'italic',
          color: '#F9FAFB',
          lineHeight: 1,
          margin: 0,
        }}>
          ihui
        </h1>
        <p style={{ fontSize: '13px', color: '#4B5563', marginTop: '1rem', textAlign: 'center' }}>
          Gobernabilidad institucional
        </p>
      </div>

      {/* Panel derecho */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '3rem',
      }}>
        <div style={{ width: '100%', maxWidth: '380px' }}>
          <h2 style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            color: '#F9FAFB',
            marginBottom: '0.5rem',
          }}>
            Iniciar sesión
          </h2>
          <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '2rem' }}>
            ihui CORE · Sistema nervioso institucional
          </p>

          {error && (
            <div style={{
              backgroundColor: '#1A0000',
              border: '1px solid #3A0000',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              marginBottom: '1.5rem',
              fontSize: '13px',
              color: '#EF4444',
            }}>
              {error}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input
              type="email"
              placeholder="Correo electrónico"
              value={email}
              onChange={e => setEmail(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                backgroundColor: '#1A1A1A',
                border: '1px solid #2A2A2A',
                color: '#F9FAFB',
                fontSize: '14px',
                outline: 'none',
              }}
            />
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                backgroundColor: '#1A1A1A',
                border: '1px solid #2A2A2A',
                color: '#F9FAFB',
                fontSize: '14px',
                outline: 'none',
              }}
            />
            <button
              onClick={handleLogin}
              disabled={loading}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                backgroundColor: loading ? '#1A3A2A' : '#2A7A5A',
                color: '#F9FAFB',
                fontSize: '14px',
                fontWeight: 600,
                border: 'none',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Entrando...' : 'Entrar →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
