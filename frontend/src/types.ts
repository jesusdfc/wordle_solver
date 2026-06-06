export type SolverStrategy = string;

export type StrategyInfo = {
  id: string;
  label: string;
  description: string;
  requires_opening_word: boolean;
  default_opening_word: string | null;
  belief_threshold: number | null;
  warning: string | null;
};

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

export type ExploreResponse = {
  secret: string;
  guesses: HistoryRow[];
  solved: boolean;
  guess_count: number;
};

export type AppMode = "menu" | "play" | "explore";

export type SuggestOptions = {
  strategy: SolverStrategy;
  openingWord?: string;
};
