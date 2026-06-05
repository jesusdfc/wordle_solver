import type { HistoryRow, SuggestResponse } from "../types";

export async function fetchSuggestion(
  history: HistoryRow[],
  strategy: string = "entropy",
): Promise<SuggestResponse> {
  const response = await fetch("/api/suggest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ history, strategy, length: 5 }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Failed to fetch suggestion");
  }

  return response.json();
}
