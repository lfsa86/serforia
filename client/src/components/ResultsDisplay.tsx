import type { QueryResponse } from '../types';
import { DataTable } from './DataTable';
import { SQLQueriesDisplay } from './SQLQueriesDisplay';
import { VisualizationDisplay } from './VisualizationDisplay';
import { Download, CheckCircle, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ResultsDisplayProps {
  results: QueryResponse | null;
}

export const ResultsDisplay = ({ results }: ResultsDisplayProps) => {
  if (!results) return null;

  const downloadCSV = () => {
    if (!results.data || results.data.length === 0) return;

    const headers = Object.keys(results.data[0]);
    const csvContent = [
      headers.join(','),
      ...results.data.map(row =>
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',')
            ? `"${value}"`
            : value;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `consulta_serfor_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Resultados de la Consulta</h2>
        {results.success ? (
          <div className="status-badge success">
            <CheckCircle size={16} />
            <span>Exitoso</span>
          </div>
        ) : (
          <div className="status-badge error">
            <AlertCircle size={16} />
            <span>Error</span>
          </div>
        )}
      </div>

      {!results.success && (
        <div className="error-message">
          <AlertCircle size={20} />
          <p>{results.error || 'Error desconocido'}</p>
        </div>
      )}

      {results.success && (
        <>
          {/* Data Table */}
          {results.data && results.data.length > 0 && (
            <div className="data-section">
              <div className="section-header">
                <h3>📊 Datos Encontrados</h3>
                <div className="metrics">
                  <span className="metric">
                    <strong>Registros:</strong> {results.data.length}
                  </span>
                  <span className="metric">
                    <strong>Columnas:</strong> {Object.keys(results.data[0]).length}
                  </span>
                </div>
              </div>
              <DataTable data={results.data} />
              <button onClick={downloadCSV} className="download-btn">
                <Download size={16} />
                Descargar CSV
              </button>
            </div>
          )}

          {/* Visualizations */}
          {results.visualization_data && results.visualization_data.length > 0 && (
            <VisualizationDisplay visualizations={results.visualization_data} />
          )}

          {/* SQL Queries */}
          {results.sql_queries && results.sql_queries.length > 0 && (
            <SQLQueriesDisplay queries={results.sql_queries} />
          )}

          {/* Response Summary */}
          <div className="response-section">
            <h3>📝 Resumen Detallado</h3>
            <div className="response-content markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {results.final_response}
              </ReactMarkdown>
            </div>
          </div>

          {/* Agents Used 
          {results.agents_used && results.agents_used.length > 0 && (
            <div className="agents-section">
              <strong>🤖 Agentes utilizados:</strong>{' '}
              {results.agents_used.join(', ')}
            </div>
          )}*/}
        </>
      )}
    </div>
  );
};
