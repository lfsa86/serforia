import { useState } from 'react';
import { Send, Lightbulb } from 'lucide-react';

interface QueryFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "¿Cuántos titulares forestales hay en total?",
  "Suma las multas registradas por departamento del titular del título habilitante",
  "Me gustaría identificar los titulares que actualmente poseen títulos habilitantes vigentes, y que además tienen infracciónes sancionadas con multas mayores a 20 UIT",
  "¿Puedes hacer un resumen de las superficies de titulo habitante según departamento?",
];

export const QueryForm = ({ onSubmit, isLoading }: QueryFormProps) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <form onSubmit={handleSubmit} className="query-form">
      <div className="form-group">
        <label htmlFor="query">Escribe tu consulta sobre datos forestales:</label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ejemplo: ¿Cuáles son las especies más comunes en la región Amazonas?"
          rows={4}
          disabled={isLoading}
        />
      </div>

      <div className="example-queries">
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
      </div>

      <button type="submit" className="submit-button" disabled={isLoading || !query.trim()}>
        <Send size={18} />
        {isLoading ? 'Procesando...' : 'Procesar Consulta'}
      </button>
    </form>
  );
};
