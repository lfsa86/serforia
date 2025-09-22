"""
Launcher script for SERFOR Streamlit app
"""
import subprocess
import sys
import os

def main():
    """Launch the Streamlit app"""
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Launch Streamlit
    try:
        print("🚀 Launching SERFOR Streamlit App...")
        print("🌐 The app will open in your browser automatically")
        print("🔗 If it doesn't open, visit: http://localhost:8501")
        print("\n" + "="*50)

        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")
        print("\nTry running manually:")
        print("streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()