"""
Pydantic models for API requests and responses
"""
import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict


# Patrones peligrosos a detectar (SQL injection, XSS, path traversal)
DANGEROUS_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|TRUNCATE)\b.*\b(FROM|INTO|TABLE)\b)",
    r"(--|\/\*|\*\/)",
    r"(\bUNION\b.*\bSELECT\b)",
    r"(<script|javascript:|on\w+\s*=)",
    r"(\.\./|\.\.\\)",
]


class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User's natural language query"
    )
    include_workflow: bool = Field(default=False, description="Include workflow details in response")

    @field_validator('query')
    @classmethod
    def validate_query_content(cls, v: str) -> str:
        """Validate query does not contain dangerous patterns"""
        normalized = ' '.join(v.upper().split())
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                raise ValueError("La consulta contiene patrones no permitidos.")
        if sum(1 for c in v if c.isalnum()) < 3:
            raise ValueError("La consulta debe contener al menos 3 caracteres alfanuméricos.")
        return v.strip()


class QueryResultSet(BaseModel):
    """Individual query result set"""
    description: str
    data: List[Dict[str, Any]]
    row_count: int
    is_primary: bool = False


class QueryResponse(BaseModel):
    """Response model for query results"""
    success: bool
    executive_response: str = ""
    final_response: str = ""
    agents_used: List[str] = []
    data: Optional[List[Dict[str, Any]]] = None  # Primary result (last query)
    query_results: Optional[List[QueryResultSet]] = None  # All query results
    visualization_data: Optional[List[Dict[str, Any]]] = None
    sql_queries: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    # Guardrails rejection fields
    rejected: Optional[bool] = None
    reason: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: str
