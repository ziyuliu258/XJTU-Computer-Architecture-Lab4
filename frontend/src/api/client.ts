import type { CacheConfig, SampleTrace, SimulateResponse } from "../types";

export async function fetchSamples(): Promise<SampleTrace[]> {
  const res = await fetch("/api/samples");
  if (!res.ok) return [];
  return res.json();
}

export async function simulate(
  traceData: string,
  config: CacheConfig,
): Promise<SimulateResponse> {
  const res = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ trace_data: traceData, config, run_sweep: true }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}
