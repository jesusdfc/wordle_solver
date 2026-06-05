import type { TileColor } from "../types";

const COLOR_CLASS: Record<TileColor, string> = {
  0: "tile-gray",
  1: "tile-yellow",
  2: "tile-green",
};

const COLOR_LABEL: Record<TileColor, string> = {
  0: "gris — no está",
  1: "amarillo — mal sitio",
  2: "verde — correcto",
};

type BoardProps = {
  word: string;
  pattern: TileColor[];
  interactive?: boolean;
  onPatternChange?: (pattern: TileColor[]) => void;
};

export function Board({
  word,
  pattern,
  interactive = false,
  onPatternChange,
}: BoardProps) {
  const cycleColor = (index: number) => {
    if (!interactive || !onPatternChange) return;
    const next = [...pattern] as TileColor[];
    next[index] = ((next[index] + 1) % 3) as TileColor;
    onPatternChange(next);
  };

  return (
    <div className="board-row" role="group" aria-label={word || "Guess row"}>
      {Array.from({ length: 5 }).map((_, index) => {
        const color = pattern[index] ?? 0;
        const letter = word[index]?.toUpperCase() ?? "";
        return (
          <button
            key={index}
            type="button"
            className={`tile ${COLOR_CLASS[color]}${interactive ? " tile-interactive" : " tile-locked"}`}
            title={interactive ? `Clic para cambiar color (${COLOR_LABEL[color]})` : undefined}
            onClick={() => cycleColor(index)}
            disabled={!interactive}
            aria-label={
              letter
                ? `${letter}, ${COLOR_LABEL[color]}`
                : `Casilla ${index + 1}, ${COLOR_LABEL[color]}`
            }
          >
            <span className="tile-letter">{letter}</span>
          </button>
        );
      })}
    </div>
  );
}

type HistoryBoardProps = {
  rows: { word: string; pattern: TileColor[] }[];
};

export function HistoryBoard({ rows }: HistoryBoardProps) {
  if (rows.length === 0) return null;

  return (
    <div className="history" aria-label="Jugadas anteriores">
      {rows.map((row, index) => (
        <Board key={index} word={row.word} pattern={row.pattern} />
      ))}
    </div>
  );
}
