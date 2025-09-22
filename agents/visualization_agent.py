"""
Visualization Agent for the SERFOR multi-agent system
Generates dynamic Streamlit visualization code based on query results
"""
import ast
import logging
import traceback
import signal
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from .base_agent import BaseAgent


class VisualizationAgent(BaseAgent):
    """Agent specialized in generating Streamlit visualization code"""

    def __init__(self):
        super().__init__(
            name="Visualization",
            role_setup="""Eres un especialista en visualizaciones Streamlit para datos SERFOR (forestales de Perú).

Generas código Python/Streamlit ejecutable que crea visualizaciones apropiadas basadas en los datos disponibles.

RESPONDE SIEMPRE con bloques de código entre etiquetas <CODIGO_STREAMLIT></CODIGO_STREAMLIT>""",
            temperature=0.3,
            max_token=3000
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization code based on query results"""
        try:
            # Extract query results
            query_results = input_data.get("query_results", [])
            user_query = input_data.get("user_query", "")

            if not query_results:
                return {"visualization_code_blocks": [], "has_visualizations": False}

            # Create DataFrame for analysis
            df_sample = pd.DataFrame(query_results)

            # Generate visualization prompt
            viz_prompt = self._build_visualization_prompt(df_sample, user_query)

            # Get code from agent
            code_response = self.run(viz_prompt)

            # Extract and clean code blocks
            code_blocks = self._extract_response_blocks(code_response, 'CODIGO_STREAMLIT')
            clean_blocks = [self._clean_code_block(code) for code in code_blocks]

            # Validate code safety
            safe_blocks = []
            for block in clean_blocks:
                if self._validate_code_safety(block):
                    safe_blocks.append(block)
                else:
                    logging.warning(f"Unsafe code block rejected: {block[:100]}...")

            logging.info(f"Generated {len(safe_blocks)} safe visualization code blocks")

            return {
                "visualization_code_blocks": safe_blocks,
                "has_visualizations": len(safe_blocks) > 0
            }

        except Exception as e:
            logging.error(f"Error in VisualizationAgent: {str(e)}")
            return {"visualization_code_blocks": [], "has_visualizations": False, "error": str(e)}

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

    def execute_visualization_code(self, code_blocks: List[str], df: pd.DataFrame) -> Dict[str, Any]:
        """Execute visualization code blocks safely"""
        # Define controlled environment
        global_vars = {
            'df': df,
            'pd': pd,
            'np': np,
            'st': st,
            'px': px,
            'len': len,
            'sum': sum,
            'max': max,
            'min': min,
            'round': round,
            'str': str,
            'int': int,
            'float': float
        }

        # Combine all code blocks
        combined_code = "\n".join(code_blocks)
        logging.debug(f"Executing visualization code:\n{combined_code}")

        try:
            # Execute with timeout protection
            self._execute_with_timeout(combined_code, global_vars, timeout=10)

            # Extract created variables (excluding initial ones)
            excluded_keys = set(global_vars.keys()) - {'df'}  # Keep df changes
            result_vars = {k: v for k, v in global_vars.items() if k not in excluded_keys}

            logging.info("Visualization code executed successfully")
            return {"success": True, "variables": result_vars}

        except Exception as e:
            error_msg = f"Error executing visualization code: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            st.error(f"Error en visualización: {str(e)}")
            return {"success": False, "error": error_msg}

    def _execute_with_timeout(self, code: str, global_vars: Dict, timeout: int = 10):
        """Execute code with timeout protection"""
        def timeout_handler(signum, frame):
            raise TimeoutError("Visualization code execution timeout")

        # Set timeout (only on Unix systems)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            exec(code, global_vars)
        except AttributeError:
            # Windows doesn't support SIGALRM, execute without timeout
            exec(code, global_vars)
        finally:
            try:
                signal.alarm(0)  # Cancel timeout
            except AttributeError:
                pass  # Windows