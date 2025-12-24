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

export interface VisualizationData {
  type: string;
  data: any; // Plotly JSON format
}

export interface QueryResultSet {
  description: string;
  data: Record<string, any>[];
  row_count: number;
  is_primary: boolean;
}

export interface QueryResponse {
  success: boolean;
  executive_response: string;
  final_response: string;
  agents_used: string[];
  data?: Record<string, any>[];  // Primary result (last query)
  query_results?: QueryResultSet[];  // All query results
  visualization_data?: VisualizationData[];
  sql_queries?: SQLQuery[];
  error?: string;
  workflow_data?: any;
}

export interface HealthResponse {
  status: string;
  database: string;
  timestamp: string;
}

export interface ViewCountInfo {
  view_name: string;
  display_name: string;
  count: number;
}

export interface ViewCountsResponse {
  success: boolean;
  views: ViewCountInfo[];
  timestamp: string;
}
