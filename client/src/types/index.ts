export interface QueryRequest {
  query: string;
  include_workflow?: boolean;
}

export interface SQLQuery {
  query: string;
  success: boolean;
  row_count?: number;
  error?: string;
  task_description: string;
}

export interface QueryResponse {
  success: boolean;
  final_response: string;
  agents_used: string[];
  data?: Record<string, any>[];
  visualization_code?: string[];
  sql_queries?: SQLQuery[];
  error?: string;
  workflow_data?: any;
}

export interface HealthResponse {
  status: string;
  database: string;
  timestamp: string;
}
