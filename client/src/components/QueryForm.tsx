import { useState } from 'react';
import { Send } from 'lucide-react';

interface QueryFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export const QueryForm = ({ onSubmit, isLoading }: QueryFormProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="query-form">
      <div className="form-group">
        <label htmlFor="query">Escribe tu consulta sobre datos forestales:</label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ejemplo: ¿Puedes hacer un resumen de las superficies de titulo habitante según departamento?"
          rows={4}
          disabled={isLoading}
        />
      </div>

      {/* <div className="example-queries">
        <div className="example-header">
          <Lightbulb size={16} />
          <span>Ejemplos de consultas:</span>
        </div>
        <div className="example-buttons">
          {EXAMPLE_QUERIES.map((example, idx) => (
            <button
              key={idx}
              type="button"
              className="example-button"
              onClick={() => handleExampleClick(example)}
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div> 
      </div>*/}

      <button type="submit" className="submit-button" disabled={isLoading || !query.trim()}>
        <Send size={18} />
        {isLoading ? 'Procesando...' : 'Procesar Consulta'}
      </button>
    </form>
  );
};
