"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str = Field(..., min_length=1, description="User's natural language query")
    include_workflow: bool = Field(default=False, description="Include workflow details in response")


class QueryResponse(BaseModel):
    """Response model for query results"""
    success: bool
    executive_response: str = ""
    final_response: str = ""
    agents_used: List[str] = []
    data: Optional[List[Dict[str, Any]]] = None
    visualization_data: Optional[List[Dict[str, Any]]] = None
    sql_queries: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: str
