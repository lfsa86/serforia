"""
Streamlit App for SERFOR Multi-Agent System - Simple Version
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from agents.orchestrator import AgentOrchestrator
from utils.logger import init_logger
from dotenv import load_dotenv

# Page config
st.set_page_config(
    page_title="SERFOR - Sistema de Consulta Forestal",
    page_icon="🌲",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #228B22);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        with st.spinner("🚀 Inicializando sistema multi-agente..."):
            load_dotenv()
            st.session_state.logger = init_logger()
            st.session_state.orchestrator = AgentOrchestrator()

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🌲 SERFOR - Sistema de Consulta Forestal</h1>
        <p style="color: #e8f5e8; margin: 0.5rem 0 0 0;">
            Sistema inteligente para consultas sobre datos forestales del Perú
        </p>
    </div>
    """, unsafe_allow_html=True)

def format_results_for_display(result_data):
    """Format and display results in a user-friendly way"""
    if not result_data.get("success"):
        st.error(f"❌ Error: {result_data.get('error', 'Error desconocido')}")
        return

    final_response = result_data.get("final_response", "")

    # Try to extract tables from the response
    execution_results = result_data.get("workflow_data", {}).get("execution_results", [])

    # Look for successful query results
    table_data = None
    for result in execution_results:
        if result.get("status") == "success" and isinstance(result.get("result"), str):
            try:
                # Try to parse JSON result from skills
                parsed_result = json.loads(result["result"])
                if parsed_result.get("success") and "data" in parsed_result:
                    table_data = parsed_result["data"]
                    break
            except:
                continue

    # Display results
    st.header("📋 Resultados de la Consulta")

    if table_data and isinstance(table_data, list) and len(table_data) > 0:
        # Display as interactive table
        st.subheader("📊 Datos Encontrados")
        df = pd.DataFrame(table_data)

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de registros", len(df))
        with col2:
            st.metric("Columnas", len(df.columns))

        # Display table with filters
        st.dataframe(df, use_container_width=True, height=400)

        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"consulta_serfor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    # Display formatted response
    st.subheader("📝 Resumen Detallado")

    # Clean the response for better display
    clean_response = final_response.replace("### ", "**").replace("#### ", "**")
    clean_response = clean_response.replace("**", "")

    # Split into sections
    sections = clean_response.split('\n\n')
    for section in sections:
        if section.strip():
            if section.startswith('|') or '|' in section:
                # Skip markdown tables as we show data tables above
                continue
            else:
                st.write(section.strip())

def main():
    """Main Streamlit app"""
    initialize_session()
    display_header()

    # Main query interface
    st.header("💬 Realizar Consulta")

    # Query input
    query = st.text_area(
        "Escribe tu consulta sobre datos forestales:",
        placeholder="Ejemplo: Necesito identificar a los titulares que tienen títulos habilitantes vigentes y que, además, cuentan con infracciones sancionadas con multas mayores a 20 UIT.",
        height=100
    )

    # Submit button
    if st.button("🚀 Procesar Consulta", type="primary", use_container_width=True):
        if query.strip():
            # Show processing
            with st.spinner("🔄 Procesando consulta..."):
                try:
                    # Execute query
                    result = st.session_state.orchestrator.process_user_query(query, True)

                    # Display results
                    format_results_for_display(result)

                    # Show agents used
                    if result.get("success"):
                        st.success(f"🤖 Agentes utilizados: {', '.join(result.get('agents_used', []))}")

                except Exception as e:
                    st.error(f"❌ Error procesando la consulta: {str(e)}")
        else:
            st.warning("⚠️ Por favor escribe una consulta antes de procesar.")

if __name__ == "__main__":
    main()