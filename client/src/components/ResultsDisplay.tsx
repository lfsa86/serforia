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
  const [isIntermediateExpanded, setIsIntermediateExpanded] = useState(false);
  const [expandedIntermediates, setExpandedIntermediates] = useState<Set<number>>(new Set());

  if (!results) return null;

  const toggleIntermediateResult = (index: number) => {
    setExpandedIntermediates(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // Get primary result (last query) and intermediate results
  // Fallback to results.data for backward compatibility
  const primaryResult = results.query_results?.find(r => r.is_primary) ||
    (results.data && results.data.length > 0 ? {
      description: "Datos Encontrados",
      data: results.data,
      row_count: results.data.length,
      is_primary: true
    } : null);
  const intermediateResults = results.query_results?.filter(r => !r.is_primary) || [];
  const hasIntermediateResults = intermediateResults.length > 0;

  const downloadCSV = (data: Record<string, any>[], filename?: string) => {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row =>
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
    a.download = filename || `consulta_serfor_${new Date().toISOString().split('T')[0]}.csv`;
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

          {/* 3. Data Section - All Results */}
          {primaryResult && primaryResult.data.length > 0 && (
            <div className="data-section-collapsible">
              <button
                className="expand-button"
                onClick={() => setIsDataExpanded(!isDataExpanded)}
              >
                <span>📊 Ver Datos Encontrados ({primaryResult.row_count} registros, {Object.keys(primaryResult.data[0]).length} columnas)</span>
                <div className="expand-button-actions">
                  <button
                    onClick={(e) => { e.stopPropagation(); downloadCSV(primaryResult.data); }}
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
                  {/* Primary Result Title & Table */}
                  <h4 className="primary-result-title">{primaryResult.description}</h4>
                  <DataTable data={primaryResult.data} />

                  {/* Intermediate Results (inside the same section) */}
                  {hasIntermediateResults && (
                    <div className="intermediate-results-section">
                      <button
                        className="expand-button secondary"
                        onClick={() => setIsIntermediateExpanded(!isIntermediateExpanded)}
                      >
                        <span>📋 Ver consultas intermedias ({intermediateResults.length})</span>
                        {isIntermediateExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                      </button>

                      {isIntermediateExpanded && (
                        <div className="intermediate-content">
                          {intermediateResults.map((result, index) => (
                            <div key={index} className="intermediate-result-item">
                              <button
                                className="intermediate-result-header"
                                onClick={() => toggleIntermediateResult(index)}
                              >
                                <span>{result.description} ({result.row_count} registros, {Object.keys(result.data[0] || {}).length} columnas)</span>
                                <div className="intermediate-result-actions">
                                  <button
                                    onClick={(e) => { e.stopPropagation(); downloadCSV(result.data, `consulta_${index + 1}_${new Date().toISOString().split('T')[0]}.csv`); }}
                                    className="download-btn-inline small"
                                    title="Descargar CSV"
                                  >
                                    <Download size={14} />
                                  </button>
                                  {expandedIntermediates.has(index) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </div>
                              </button>
                              {expandedIntermediates.has(index) && (
                                <div className="intermediate-result-data">
                                  <DataTable data={result.data} />
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
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
