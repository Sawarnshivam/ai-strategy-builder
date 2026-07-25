/** API calls for parameter-sweep optimization. */

import { apiRequest } from "@/lib/api-client";
import type { SweepRequest, SweepResponse } from "@/types/optimize";

/** Run a parameter sweep and return the ranked configurations. */
export function runSweep(request: SweepRequest): Promise<SweepResponse> {
  return apiRequest<SweepResponse>("/optimize/sweep", {
    method: "POST",
    body: request,
  });
}