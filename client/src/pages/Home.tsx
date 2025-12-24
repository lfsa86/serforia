import { useState, useEffect, useRef } from 'react';
import { QueryForm } from '../components/QueryForm';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { queryApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import type { QueryResponse, ViewCountInfo } from '../types';
import '../App.css';

export const Home = () => {
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewCounts, setViewCounts] = useState<ViewCountInfo[]>([]);
  const { user, logout } = useAuth();
  const resultsRef = useRef<HTMLDivElement>(null);

  // Cargar los conteos de las vistas al montar el componente
  useEffect(() => {
    const fetchViewCounts = async () => {
      try {
        const response = await queryApi.getViewCounts();
        if (response.success) {
          setViewCounts(response.views);
        }
      } catch (err) {
        console.error('Error fetching view counts:', err);
        // Silently fail - the UI will show without counts
      }
    };

    fetchViewCounts();
  }, []);

  // Helper para obtener el conteo de una vista por su nombre de display
  const getCountByDisplayName = (displayName: string): number | null => {
    const view = viewCounts.find(v => v.display_name === displayName);
    return view ? view.count : null;
  };

  // Helper para formatear el conteo
  const formatCount = (count: number | null): string => {
    if (count === null) return '';
    return ` (${count.toLocaleString('es-PE')} registros)`;
  };

  const handleQuerySubmit = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await queryApi.processQuery({
        query,
        include_workflow: false,
      });
      setResults(response);

      // Scroll automático hacia los resultados después de un breve delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      setResults({
        success: false,
        executive_response: '',
        final_response: '',
        agents_used: [],
        error: errorMessage,
      });

      // También hacer scroll en caso de error
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>SERFORia- Sistema de Consulta Forestal v1.0</h1>
          <p>Sistema inteligente para consultas sobre datos forestales del Perú</p>
        </div>
        <div className="user-info">
          <span>Bienvenido, {user?.nombre}</span>
          <button onClick={logout} className="logout-button">
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="app-main">
        <section className="welcome-section">
          <h2>¡Bienvenido!</h2>
          <p>Esta aplicación te permite consultar la base de datos de la DIR sobre:</p>
          <ul>
            <li>
              <strong>Autorizaciones:</strong> CTP{formatCount(getCountByDisplayName('Autorizaciones CTP'))},
              desbosque{formatCount(getCountByDisplayName('Autorizaciones de desbosque'))},
              depósito{formatCount(getCountByDisplayName('Autorizaciones de depósito'))} y
              cambio de uso{formatCount(getCountByDisplayName('Cambios de uso'))}
            </li>
            <li><strong>Títulos habilitantes</strong>{formatCount(getCountByDisplayName('Títulos habilitantes'))}</li>
            <li><strong>Plantaciones forestales</strong>{formatCount(getCountByDisplayName('Plantaciones forestales'))}</li>
            <li><strong>Licencias de caza</strong>{formatCount(getCountByDisplayName('Licencias de caza'))}</li>
            <li><strong>Infractores</strong>{formatCount(getCountByDisplayName('Infractores'))}</li>
          </ul>
          <p className="welcome-hint">
            Solo escribe tu consulta -por ejemplo: <em>"¿Qué títulos habilitantes están vigentes en Loreto?"</em> o <em>"Muéstrame las plantaciones asociadas a titulares con sanciones"</em>- y el sistema generará automáticamente la consulta y mostrará los resultados.
          </p>
        </section>

        <section className="query-section">
          <h2>Realizar Consulta</h2>
          <QueryForm onSubmit={handleQuerySubmit} isLoading={isLoading} />
        </section>

        <div ref={resultsRef}>
          {isLoading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Procesando consulta...</p>
            </div>
          )}

          {error && !results && (
            <div className="error-container">
              <p>Error: {error}</p>
            </div>
          )}

          <ResultsDisplay results={results} />
        </div>
      </main>
    </div>
  );
};
