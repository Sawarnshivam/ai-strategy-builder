/** Shape returned by GET /health on the FastAPI backend. */
export interface HealthResponse {
  status: string;
  app_name: string;
  environment: string;
  version: string;
}