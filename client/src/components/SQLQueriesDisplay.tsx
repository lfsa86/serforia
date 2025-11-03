import { useState } from 'react';
import type { SQLQuery } from '../types';
import { ChevronDown, ChevronUp, CheckCircle, XCircle } from 'lucide-react';

interface SQLQueriesDisplayProps {
  queries: SQLQuery[];
}

export const SQLQueriesDisplay = ({ queries }: SQLQueriesDisplayProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="sql-queries-section">
      <button
        className="expand-button"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>🔍 Ver Queries SQL Ejecutadas ({queries.length})</span>
        {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {isExpanded && (
        <div className="queries-content">
          {queries.map((query, idx) => (
            <div key={idx} className="query-item">
              <div className="query-header">
                <h4>Query {idx + 1}: {query.task_description}</h4>
                {query.success ? (
                  <div className="status-badge success">
                    <CheckCircle size={16} />
                    <span>Exitosa - {query.row_count} filas</span>
                  </div>
                ) : (
                  <div className="status-badge error">
                    <XCircle size={16} />
                    <span>Error: {query.error}</span>
                  </div>
                )}
              </div>
              <pre className="sql-code">
                <code>{query.query}</code>
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
