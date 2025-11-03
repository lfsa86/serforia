"""
Query routes for the API
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import pyodbc

from ..models import QueryRequest, QueryResponse, HealthResponse
from ..services import get_orchestrator_service
from ..core import settings

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query about forestry data

    Args:
        request: QueryRequest containing the user's query

    Returns:
        QueryResponse with results, data, and metadata
    """
    try:
        orchestrator_service = get_orchestrator_service()
        result = orchestrator_service.process_query(
            query=request.query,
            include_workflow=request.include_workflow
        )

        return QueryResponse(**result)

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌❌❌ ERROR in query route:")
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API and database connectivity

    Returns:
        HealthResponse with status information
    """
    db_status = "disconnected"

    try:
        # Test database connection
        conn = pyodbc.connect(settings.database_url, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        database=db_status,
        timestamp=datetime.now().isoformat()
    )
