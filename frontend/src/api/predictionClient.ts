import type { PredictionRequest, PredictionResponse } from "../types/prediction";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {}

export async function predictPrice(
  payload: PredictionRequest,
): Promise<PredictionResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError("Could not reach the prediction server. Is the backend running?");
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch {
      // ignore body parse errors
    }
    throw new ApiError(detail);
  }

  return response.json() as Promise<PredictionResponse>;
}

export async function fetchLocations(): Promise<string[]> {
  const response = await fetch("/locations.json");
  if (!response.ok) return [];
  return response.json() as Promise<string[]>;
}
