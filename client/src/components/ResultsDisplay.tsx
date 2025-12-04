import { useState } from 'react';
import type { QueryResponse } from '../types';
import { DataTable } from './DataTable';
import { SQLQueriesDisplay } from './SQLQueriesDisplay';
import { VisualizationDisplay } from './VisualizationDisplay';
import { Download, CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ResultsDisplayProps {
  results: QueryResponse | null;
}

export const ResultsDisplay = ({ results }: ResultsDisplayProps) => {
  const [isDataExpanded, setIsDataExpanded] = useState(false);

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
          {/* 1. Executive Response - Main focus for executives */}
          {results.executive_response && (
            <div className="executive-response-section">
              <h3>Respuesta</h3>
              <div className="executive-response-content">
                <p>{results.executive_response}</p>
              </div>
            </div>
          )}

          {/* 2. SQL Queries (collapsible, closed by default) */}
          {results.sql_queries && results.sql_queries.length > 0 && (
            <SQLQueriesDisplay queries={results.sql_queries} />
          )}

          {/* 3. Data Table (collapsible, closed by default) */}
          {results.data && results.data.length > 0 && (
            <div className="data-section-collapsible">
              <button
                className="expand-button"
                onClick={() => setIsDataExpanded(!isDataExpanded)}
              >
                <span>📊 Ver Datos Encontrados ({results.data.length} registros, {Object.keys(results.data[0]).length} columnas)</span>
                <div className="expand-button-actions">
                  <button
                    onClick={(e) => { e.stopPropagation(); downloadCSV(); }}
                    className="download-btn-inline"
                    title="Descargar CSV"
                  >
                    <Download size={16} />
                    CSV
                  </button>
                  {isDataExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
              </button>

              {isDataExpanded && (
                <div className="data-content">
                  <DataTable data={results.data} />
                </div>
              )}
            </div>
          )}

          {/* 4. Detailed Response */}
          {results.final_response && (
            <div className="response-section">
              <h3>Análisis Detallado</h3>
              <div className="response-content markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {results.final_response}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {/* 5. Visualizations */}
          {results.visualization_data && results.visualization_data.length > 0 && (
            <VisualizationDisplay visualizations={results.visualization_data} />
          )}
        </>
      )}
    </div>
  );
};
