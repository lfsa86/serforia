import { useState } from 'react';
import { QueryForm } from './components/QueryForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { queryApi } from './services/api';
import type { QueryResponse } from './types';
import './App.css';

function App() {
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      setResults({
        success: false,
        final_response: '',
        agents_used: [],
        error: errorMessage,
      });
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
      </header>

      <main className="app-main">
        <section className="welcome-section">
          <h2>¡Bienvenido!</h2>
          <p>Esta aplicación te permite consultar la base de datos de la DIR sobre:</p>
          <ul>
            <li><strong>Autorizaciones:</strong> CTP, desbosque, depósito y cambio de uso</li>
            <li><strong>Títulos habilitantes</strong></li>
            <li><strong>Plantaciones forestales</strong></li>
            <li><strong>Licencias de caza</strong></li>
            <li><strong>Infractores</strong></li>
          </ul>
          <p className="welcome-hint">
            Solo escribe tu consulta -por ejemplo: <em>"¿Qué títulos habilitantes están vigentes en Loreto?"</em> o <em>"Muéstrame las plantaciones asociadas a titulares con sanciones"</em>- y el sistema generará automáticamente la consulta y mostrará los resultados.
          </p>
        </section>

        <section className="query-section">
          <h2>Realizar Consulta</h2>
          <QueryForm onSubmit={handleQuerySubmit} isLoading={isLoading} />
        </section>

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
      </main>
    </div>
  );
}

export default App;
