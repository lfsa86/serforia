"""
Visualization Agent for the SERFOR multi-agent system
Now simplified for API mode - visualizations handled by React frontend
"""
import ast
import logging
from typing import Dict, Any, List
import pandas as pd

from .base_agent import BaseAgent


class VisualizationAgent(BaseAgent):
    """Agent specialized in analyzing data for visualization recommendations"""

    def __init__(self):
        super().__init__(
            name="Visualization",
            role_setup="""Eres un analista de datos especializado en recomendar visualizaciones para datos SERFOR.

Tu trabajo es analizar los datos y devolver recomendaciones simples, NO código ejecutable.
Las visualizaciones se implementarán en el frontend React.""",
            temperature=0.3,
            max_token=1500
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplified processing - no code generation, just data analysis
        Visualizations are now handled by the React frontend
        """
        try:
            query_results = input_data.get("query_results", [])

            if not query_results:
                return {"has_visualizations": False}

            # Just return empty - frontend handles visualizations
            logging.info("Visualization processing skipped - handled by frontend")

            return {
                "has_visualizations": False,
                "message": "Visualizations handled by frontend"
            }

        except Exception as e:
            logging.error(f"Error in VisualizationAgent: {str(e)}")
            return {"has_visualizations": False, "error": str(e)}

    def execute_visualization_code(self, code_blocks: List[str], df: pd.DataFrame) -> Dict[str, Any]:
        """
        Visualization execution disabled for API mode.
        Visualizations are now handled by the React frontend.
        """
        logging.info("Visualization execution skipped - handled by frontend")
        return {
            "success": True,
            "message": "Visualizations handled by frontend",
            "code_blocks": []
        }

    # Legacy methods kept for compatibility but not used
    def _build_visualization_prompt(self, df: pd.DataFrame, user_query: str) -> str:
        """Build prompt with simple data + detailed instructions"""
        sample_data = df.head(3).to_dict('records') if len(df) > 0 else []

        return f"""
Eres un especialista en visualizaciones Streamlit para datos SERFOR (forestales de Perú).

CONSULTA USUARIO: "{user_query}"
COLUMNAS DISPONIBLES: {list(df.columns)}
MUESTRA DE DATOS: {sample_data}
TOTAL FILAS: {len(df)}

TU TRABAJO:
1. ANALIZAR los datos y determinar visualizaciones apropiadas
2. GENERAR código Python/Streamlit ejecutable
3. CREAR 2-4 visualizaciones complementarias + métricas clave
4. USAR títulos descriptivos con emojis relevantes

TIPOS DE VISUALIZACIÓN SEGÚN DATOS:
- st.bar_chart() → Conteos (titulares, especies, regiones)
- st.line_chart() → Tendencias temporales (multas por año)
- px.histogram() → Distribuciones (montos, superficies)
- px.scatter() → Correlaciones (superficie vs multa)
- st.metric() → KPIs importantes

REGLAS CRÍTICAS:
✅ USA la variable 'df' (ya disponible)
✅ VALIDA columnas antes de usar: if 'columna' in df.columns:
✅ MANEJA casos con pocos datos: if len(df) > 5:
❌ NO uses imports (todo está disponible)
❌ NO generes datos ficticios

EJEMPLO DE RESPUESTA:

<CODIGO_STREAMLIT>
# Métricas principales
if len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Registros", len(df))

    if 'TX_NombreTitular' in df.columns:
        with col2:
            st.metric("👥 Titulares Únicos", df['TX_NombreTitular'].nunique())

    if 'NU_MultaUIT' in df.columns:
        with col3:
            st.metric("💰 Multa Total", f"{{df['NU_MultaUIT'].sum():.1f}} UIT")

# Visualización principal
if 'TX_NombreTitular' in df.columns and len(df) > 5:
    st.subheader("📊 Top 10 Titulares con Más Registros")
    top_titulares = df['TX_NombreTitular'].value_counts().head(10)
    st.bar_chart(top_titulares)

# Distribución si hay datos numéricos
if 'NU_MultaUIT' in df.columns and len(df) > 10:
    st.subheader("💰 Distribución de Multas")
    fig = px.histogram(df, x='NU_MultaUIT', title="Distribución de Multas (UIT)")
    st.plotly_chart(fig, use_container_width=True)
</CODIGO_STREAMLIT>

Responde SOLO con bloques <CODIGO_STREAMLIT>, sin explicaciones adicionales.
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