export type TileColor = 0 | 1 | 2;

export type HistoryRow = {
  word: string;
  pattern: TileColor[];
};

export type SuggestResponse = {
  suggestion: string;
  remaining: number;
  solved: boolean;
  candidates: string[] | null;
};

export type BenchmarkResponse = {
  secret: string;
  guesses: HistoryRow[];
  solved: boolean;
  guess_count: number;
};

export type AppMode = "menu" | "play" | "benchmark";
