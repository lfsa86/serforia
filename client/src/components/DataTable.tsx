interface DataTableProps {
  data: Record<string, any>[];
}

// Detecta si un valor es una fecha/datetime
const isDateValue = (value: unknown): boolean => {
  if (typeof value !== 'string') return false;
  // ISO date format (2024-01-15, 2024-01-15T10:30:00)
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}(T|\s)/;
  // Common date formats (15/01/2024, 01-15-2024)
  const commonDatePattern = /^\d{2}[/-]\d{2}[/-]\d{4}/;
  return isoDatePattern.test(value) || commonDatePattern.test(value);
};

// Formatea valores numéricos con separadores de miles y decimales
const formatValue = (value: unknown): string => {
  if (value === null || value === undefined) return '-';

  // No formatear fechas
  if (isDateValue(value)) return String(value);

  // Formatear números
  if (typeof value === 'number') {
    // Enteros: sin decimales, con separador de miles
    if (Number.isInteger(value)) {
      return value.toLocaleString('en-US');
    }
    // Decimales: 2 decimales, con separador de miles
    return value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  // Strings que parecen números (vienen del backend como string)
  if (typeof value === 'string' && !isNaN(Number(value)) && value.trim() !== '') {
    const num = Number(value);
    if (Number.isInteger(num)) {
      return num.toLocaleString('en-US');
    }
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  return String(value);
};

export const DataTable = ({ data }: DataTableProps) => {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((column) => (
                <td key={column}>{formatValue(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
