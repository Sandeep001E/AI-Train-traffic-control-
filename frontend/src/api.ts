// Pick API base automatically:
// - Dev (Vite): talk directly to FastAPI on localhost:8000
// - Prod (Docker/nginx): use relative path so nginx proxies /api/ to backend
// - If VITE_API_BASE is set, that always wins
const API_BASE: string =
  (import.meta as any).env?.VITE_API_BASE ||
  ((import.meta as any).env?.DEV ? 'http://localhost:8000/api/v1' : '/api/v1');

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = {
    // Only set Content-Type when sending a body (avoids some preflight issues on GET)
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {}),
  };

  let res: Response;
  try {
    res = await fetch(url, { ...options, headers });
  } catch (err: any) {
    // Network/CORS/DNS failure -> browser throws TypeError: Failed to fetch
    const msg = err?.message || 'Failed to fetch';
    throw new Error(`Network error calling ${url}: ${msg}. Check that the backend is running and that CORS/URL are correct (API_BASE=${API_BASE}).`);
  }
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return res.json();
  }
  // @ts-ignore
  return res.text();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: any) => request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body?: any) => request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};

export type Train = {
  id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  status?: string;
  priority?: number;
  max_speed?: number;
  origin_station?: string;
  destination_station?: string;
};

export type Section = {
  id: number;
  section_code: string;
  section_name: string;
  start_station: string;
  end_station: string;
  length_km: number;
};

export type OptimizeResponse = {
  schedule: Array<{ train_id: number; planned_entry: string; planned_exit: string; }>;
  metrics: { throughput_per_hour: number; average_headway_minutes: number };
};

export type OROptimizeResult = {
  status?: string;
  objective?: number;
  schedule: Array<{ train_id: number; planned_entry: string; planned_exit: string; }>;
  metrics: { throughput_per_hour: number; average_headway_minutes: number };
};

export type KPIs = {
  punctuality_rate: number;
  average_delay_minutes: number;
  section_throughput_per_hour: number;
  resource_utilization_percent: number;
  conflict_resolution_time_seconds: number;
};
