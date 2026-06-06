import type {
  ExploreResponse,
  HistoryRow,
  StrategyInfo,
  SuggestOptions,
  SuggestResponse,
} from "../types";

const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

function apiUrl(path: string): string {
  return API_BASE ? `${API_BASE}${path}` : path;
}

function parseErrorDetail(body: { detail?: string | { msg: string }[] }): string {
  const { detail } = body;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return "Request failed";
}

export async function fetchStrategies(): Promise<StrategyInfo[]> {
  const response = await fetch(apiUrl("/api/strategies"));
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(parseErrorDetail(body));
  }
  return response.json();
}

export async function fetchSuggestion(
  history: HistoryRow[],
  options: SuggestOptions,
): Promise<SuggestResponse> {
  const { strategy, openingWord } = options;
  const response = await fetch(apiUrl("/api/suggest"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      history,
      length: 5,
      strategy,
      opening_word: openingWord ?? null,
    }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(parseErrorDetail(body));
  }

  return response.json();
}

export async function fetchExplore(
  secret: string,
  options: SuggestOptions,
): Promise<ExploreResponse> {
  const { strategy, openingWord } = options;
  const response = await fetch(apiUrl("/api/explore"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      secret,
      length: 5,
      max_guesses: 6,
      strategy,
      opening_word: openingWord ?? null,
    }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(parseErrorDetail(body));
  }

  return response.json();
}
