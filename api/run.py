"""
Development server runner
"""
import uvicorn
from dotenv import load_dotenv
from app.core import settings

if __name__ == "__main__":
    load_dotenv()

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
