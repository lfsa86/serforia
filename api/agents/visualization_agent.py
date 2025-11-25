"""
Visualization Agent for the SERFOR multi-agent system
Generates Plotly visualizations and exports them as JSON for React frontend
"""
import ast
import logging
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

from .base_agent import BaseAgent


class VisualizationAgent(BaseAgent):
    """Agent specialized in generating Plotly visualizations for SERFOR data"""

    def __init__(self):
        super().__init__(
            name="Visualization",
            role_setup="""Eres un especialista en visualizaciones Plotly para datos SERFOR (forestales de Perú).

Tu trabajo es analizar los datos y generar código Python/Plotly ejecutable que cree visualizaciones informativas.
Las visualizaciones se exportarán como JSON para renderizarse en el frontend React con react-plotly.js.""",
            temperature=0.3,
            max_token=2000
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Plotly visualizations from query results and export as JSON
        """
        try:
            query_results = input_data.get("query_results", [])
            user_query = input_data.get("user_query", "")

            if not query_results or len(query_results) == 0:
                return {"has_visualizations": False}

            # Convert to DataFrame
            df = pd.DataFrame(query_results)

            # Generate visualization code
            logging.info(f"Generating visualizations for {len(df)} rows, {len(df.columns)} columns")
            prompt = self._build_visualization_prompt(df, user_query)
            response = self.run(prompt)

            # Extract code blocks
            code_blocks = self._extract_response_blocks(response, "CODIGO_PLOTLY")

            if not code_blocks:
                logging.warning("No visualization code blocks found in agent response")
                return {"has_visualizations": False}

            # Execute code and capture figures
            viz_data = self._execute_and_capture_figures(code_blocks, df)

            return {
                "has_visualizations": len(viz_data) > 0,
                "visualization_data": viz_data,
                "visualization_count": len(viz_data)
            }

        except Exception as e:
            logging.error(f"Error in VisualizationAgent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"has_visualizations": False, "error": str(e)}

    def _execute_and_capture_figures(self, code_blocks: List[str], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Execute visualization code blocks and capture Plotly figures as JSON
        """
        viz_data = []

        for i, code_block in enumerate(code_blocks):
            try:
                # Clean the code
                code = self._clean_code_block(code_block)

                # Validate safety
                if not self._validate_code_safety(code):
                    logging.warning(f"Code block {i+1} failed safety validation")
                    continue

                # Create execution namespace
                namespace = {
                    'df': df,
                    'pd': pd,
                    'px': px,
                    'go': go,
                    'figures': []  # List to collect figures
                }

                # Wrap code to capture figures
                wrapped_code = self._wrap_code_to_capture_figures(code)

                # Execute the code
                exec(wrapped_code, namespace)

                # Extract captured figures
                figures = namespace.get('figures', [])

                for fig in figures:
                    if hasattr(fig, 'to_json'):
                        # Convert Plotly figure to JSON
                        fig_json = fig.to_json()
                        viz_data.append({
                            "type": "plotly",
                            "data": json.loads(fig_json)
                        })
                        logging.info(f"Captured Plotly figure from code block {i+1}")

            except Exception as e:
                logging.error(f"Error executing visualization code block {i+1}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        return viz_data

    def _wrap_code_to_capture_figures(self, code: str) -> str:
        """
        Wrap code to capture Plotly figure objects
        """
        # Replace common Plotly creation patterns to capture figures
        wrapped = code

        # Pattern 1: fig = px.something() or fig = go.Figure()
        # Already creates a 'fig' variable, we'll capture it at the end

        # Pattern 2: Direct plotting without assignment
        # We need to look for px.* or go.Figure() calls

        # Add capture logic at the end
        capture_code = """
# Capture any figure created
if 'fig' in locals():
    figures.append(fig)
"""

        return wrapped + "\n" + capture_code

    def execute_visualization_code(self, code_blocks: List[str], df: pd.DataFrame) -> Dict[str, Any]:
        """
        Legacy method - kept for compatibility with Streamlit version
        """
        viz_data = self._execute_and_capture_figures(code_blocks, df)
        return {
            "success": len(viz_data) > 0,
            "visualization_data": viz_data,
            "message": f"Generated {len(viz_data)} visualizations"
        }

    def _build_visualization_prompt(self, df: pd.DataFrame, user_query: str) -> str:
        """Build prompt to generate Plotly visualization code"""
        sample_data = df.head(3).to_dict('records') if len(df) > 0 else []

        return f"""
Eres un especialista en visualizaciones Plotly para datos SERFOR (forestales de Perú).

CONSULTA USUARIO: "{user_query}"
COLUMNAS DISPONIBLES: {list(df.columns)}
MUESTRA DE DATOS: {sample_data}
TOTAL FILAS: {len(df)}

TU TRABAJO:
1. ANALIZAR los datos y determinar 2-3 visualizaciones apropiadas
2. GENERAR código Python/Plotly ejecutable
3. Cada visualización debe asignarse a una variable 'fig'
4. USAR títulos descriptivos en español

TIPOS DE VISUALIZACIÓN SEGÚN DATOS:
- px.bar() → Conteos, comparaciones (titulares, especies, regiones)
- px.line() → Tendencias temporales (multas por año)
- px.histogram() → Distribuciones (montos, superficies)
- px.scatter() → Correlaciones (superficie vs multa)
- px.pie() → Proporciones

REGLAS CRÍTICAS:
✅ USA la variable 'df' (ya disponible)
✅ VALIDA columnas antes de usar: if 'columna' in df.columns:
✅ MANEJA casos con pocos datos: if len(df) > 5:
✅ CADA gráfico debe asignarse a 'fig': fig = px.bar(...)
✅ Importa px y go ya están disponibles
❌ NO uses imports
❌ NO generes datos ficticios
❌ NO uses st.plotly_chart() ni ninguna función de Streamlit

EJEMPLO DE RESPUESTA:

<CODIGO_PLOTLY>
# Visualización 1: Top 10 Titulares
if 'TX_NombreTitular' in df.columns and len(df) > 5:
    top_titulares = df['TX_NombreTitular'].value_counts().head(10)
    fig = px.bar(
        x=top_titulares.index,
        y=top_titulares.values,
        title="Top 10 Titulares con Más Registros",
        labels={{'x': 'Titular', 'y': 'Registros'}}
    )
</CODIGO_PLOTLY>

<CODIGO_PLOTLY>
# Visualización 2: Distribución de Multas
if 'NU_MultaUIT' in df.columns and len(df) > 10:
    fig = px.histogram(
        df,
        x='NU_MultaUIT',
        title="Distribución de Multas (UIT)",
        labels={{'NU_MultaUIT': 'Multa (UIT)'}}
    )
</CODIGO_PLOTLY>

Responde SOLO con bloques <CODIGO_PLOTLY>, sin explicaciones adicionales.
Genera 2-3 visualizaciones relevantes según los datos disponibles.
"""

    def _extract_response_blocks(self, response: str, block_type: str) -> List[str]:
        """Extract code blocks from agent response"""
        blocks = []
        lines = response.split('\n')
        in_block = False
        current_block = []

        start_tag = f"<{block_type}>"
        end_tag = f"</{block_type}>"

        for line in lines:
            if start_tag in line:
                in_block = True
                continue
            elif end_tag in line:
                in_block = False
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
            elif in_block:
                current_block.append(line)

        return blocks

    def _clean_code_block(self, code_block: str) -> str:
        """Clean code block removing markdown delimiters"""
        return code_block.replace('```python', '').replace('```', '').strip()

    def _validate_code_safety(self, code: str) -> bool:
        """Validate code safety with multiple checks"""
        # Blacklist dangerous patterns
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess',
            '__import__', 'eval(', 'open(', 'file(',
            'requests.', 'urllib.', 'socket.',
            'exec(', '__builtins__', 'globals(',
            'locals(', 'vars(', 'dir('
        ]

        if any(pattern in code for pattern in dangerous_patterns):
            logging.warning(f"Dangerous pattern found in code")
            return False

        # AST validation
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    logging.warning(f"Import statement found in code")
                    return False
        except SyntaxError:
            logging.warning(f"Syntax error in code")
            return False

        return True