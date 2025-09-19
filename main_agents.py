"""
Main entry point for the SERFOR multi-agent system
"""
from agents.orchestrator import AgentOrchestrator
from utils.logger import init_logger
from dotenv import load_dotenv

def main():
    """Main function to run the SERFOR agent system"""

    # Load environment variables
    load_dotenv()

    # Initialize logging system
    logger = init_logger()
    print(f"📝 Sistema de logging inicializado - Session ID: {logger.session_id}")

    # Initialize orchestrator
    print("🚀 Inicializando sistema multi-agente SERFOR...")
    orchestrator = AgentOrchestrator()

    # Test agents
    print("\n🔧 Probando conectividad de agentes...")
    test_results = orchestrator.test_agents()

    for agent_name, is_working in test_results.items():
        status = "✅ OK" if is_working else "❌ ERROR"
        print(f"  {agent_name}: {status}")

    # Show agent info
    print("\n📊 Información de agentes:")
    agent_info = orchestrator.get_agent_info()
    for name, info in agent_info.items():
        print(f"  {name}: {info['role'][:50]}...")

    # Interactive loop
    print("\n" + "="*60)
    print("🌲 SISTEMA SERFOR - Consulta de Datos Forestales")
    print("="*60)
    print("Escribe 'salir' para terminar\n")

    while True:
        try:
            user_query = input("💬 Tu consulta: ").strip()

            if user_query.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break

            if not user_query:
                continue

            print(f"\n🔄 Procesando: '{user_query}'\n")

            # Process query through agent pipeline
            result = orchestrator.process_user_query(user_query)

            if result["success"]:
                print("="*60)
                print("📋 RESPUESTA:")
                print("="*60)
                print(result["final_response"])
                print("\n" + "="*60)
                print(f"🤖 Agentes utilizados: {', '.join(result['agents_used'])}")

                # Show logging information
                log_summary = logger.get_session_summary()
                print(f"📊 Session summary: {log_summary['queries_count']} queries, {log_summary['sql_queries_count']} SQL queries, {log_summary['errors_count']} errors")
                print(f"📁 Logs guardados en: {log_summary['log_files']['detailed_log']}")
            else:
                print(f"❌ Error procesando consulta: {result['error']}")

            print("\n")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()