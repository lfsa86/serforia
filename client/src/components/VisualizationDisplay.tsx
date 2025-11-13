import type { VisualizationData } from '../types';
import Plot from 'react-plotly.js';

interface VisualizationDisplayProps {
  visualizations: VisualizationData[];
}

export const VisualizationDisplay = ({ visualizations }: VisualizationDisplayProps) => {
  if (!visualizations || visualizations.length === 0) {
    return null;
  }

  return (
    <div className="visualization-section">
      <h3>📈 Visualizaciones</h3>
      <div className="visualizations-grid">
        {visualizations.map((viz, index) => (
          <div key={index} className="visualization-item">
            {viz.type === 'plotly' && viz.data && (
              <Plot
                data={viz.data.data || []}
                layout={{
                  ...viz.data.layout,
                  autosize: true,
                  margin: { l: 50, r: 50, t: 50, b: 50 }
                }}
                config={{
                  responsive: true,
                  displayModeBar: true,
                  displaylogo: false,
                  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                }}
                style={{ width: '100%', height: '400px' }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
