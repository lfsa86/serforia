"""
Query routes for the API
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
import time
import pyodbc
import logging

from ..models import QueryRequest, QueryResponse, HealthResponse, ViewCountInfo, ViewCountsResponse, UserInfo
from ..services import get_orchestrator_service, get_wazuh_logger
from ..core import settings
from ..dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    req: Request,
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Process a natural language query about forestry data

    Args:
        request: QueryRequest containing the user's query

    Returns:
        QueryResponse with results, data, and metadata
    """
    wazuh = get_wazuh_logger()
    client_ip = req.client.host if req.client else "unknown"
    start_time = time.time()

    try:
        orchestrator_service = get_orchestrator_service()
        result = orchestrator_service.process_query(
            query=request.query,
            include_workflow=request.include_workflow
        )

        response_time_ms = int((time.time() - start_time) * 1000)

        # Extract SQL queries from result
        sql_queries = []
        if result.get("sql_queries"):
            for sq in result["sql_queries"]:
                if isinstance(sq, dict) and sq.get("query"):
                    sql_queries.append(sq["query"])
                elif isinstance(sq, str):
                    sql_queries.append(sq)

        # Check if query was rejected by guardrails
        is_rejected = result.get("rejected", False)
        rejection_reason = result.get("reason") if is_rejected else None

        # Log to WAZUH
        wazuh.log_query(
            user_id=current_user.id,
            user_name=current_user.nombre,
            source_ip=client_ip,
            natural_query=request.query,
            sql_queries=sql_queries if sql_queries else None,
            http_status=200,
            success=result.get("success", True),
            response_time_ms=response_time_ms,
            rejected=is_rejected,
            rejection_reason=rejection_reason
        )

        return QueryResponse(**result)

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"Query error: {error_detail}")

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log error to WAZUH (internal - includes full error)
        wazuh.log_query(
            user_id=current_user.id,
            user_name=current_user.nombre,
            source_ip=client_ip,
            natural_query=request.query,
            sql_queries=None,
            http_status=500,
            success=False,
            error_message=str(e),
            response_time_ms=response_time_ms
        )

        # Return generic error to client (don't expose internal details)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor, intente nuevamente."
        )


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
        # Log error internally but don't expose details to client
        logger.error(f"Health check DB error: {str(e)}")
        db_status = "error"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=datetime.now().isoformat()
    )


@router.get("/views/counts", response_model=ViewCountsResponse)
async def get_view_counts(
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Get row counts for all available database views

    Returns:
        ViewCountsResponse with counts for each view
    """
    # Mapping of view names to display names (as shown in the UI)
    view_mappings = {
        "V_AUTORIZACION_CTP": "Autorizaciones CTP",
        "V_AUTORIZACION_DEPOSITO": "Autorizaciones de depósito",
        "V_AUTORIZACION_DESBOSQUE": "Autorizaciones de desbosque",
        "V_CAMBIO_USO": "Cambios de uso",
        "V_TITULOHABILITANTE": "Títulos habilitantes",
        "V_PLANTACION": "Plantaciones forestales",
        "V_LICENCIA_CAZA": "Licencias de caza",
        "V_INFRACTOR": "Infractores"
    }

    view_counts = []

    try:
        conn = pyodbc.connect(settings.database_url, timeout=10)
        cursor = conn.cursor()

        for view_name, display_name in view_mappings.items():
            try:
                # Get count for each view (views are in Dir schema, not dbo)
                count_query = f"SELECT COUNT(*) FROM Dir.[{view_name}]"
                result = cursor.execute(count_query).fetchone()
                count = result[0] if result else 0

                view_counts.append(ViewCountInfo(
                    view_name=view_name,
                    display_name=display_name,
                    count=count
                ))

            except Exception as e:
                logger.warning(f"Error getting count for {view_name}: {str(e)}")
                # Add with count 0 if query fails
                view_counts.append(ViewCountInfo(
                    view_name=view_name,
                    display_name=display_name,
                    count=0
                ))

        cursor.close()
        conn.close()

        return ViewCountsResponse(
            success=True,
            views=view_counts,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error getting view counts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener conteos de vistas"
        )
