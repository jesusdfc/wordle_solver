import type { TileColor } from "../types";

const COLOR_CLASS: Record<TileColor, string> = {
  0: "tile-gray",
  1: "tile-yellow",
  2: "tile-green",
};

const COLOR_LABEL: Record<TileColor, string> = {
  0: "gray",
  1: "yellow",
  2: "green",
};

type BoardProps = {
  word: string;
  pattern: TileColor[];
  editable?: boolean;
  onWordChange?: (word: string) => void;
  onPatternChange?: (pattern: TileColor[]) => void;
};

export function Board({
  word,
  pattern,
  editable = false,
  onWordChange,
  onPatternChange,
}: BoardProps) {
  const cycleColor = (index: number) => {
    if (!editable || !onPatternChange) return;
    const next = [...pattern] as TileColor[];
    next[index] = ((next[index] + 1) % 3) as TileColor;
    onPatternChange(next);
  };

  const updateLetter = (index: number, letter: string) => {
    if (!editable || !onWordChange) return;
    const chars = word.padEnd(5, " ").split("");
    chars[index] = letter.slice(-1).toLowerCase();
    onWordChange(chars.join("").trimEnd());
  };

  return (
    <div className="board-row">
      {Array.from({ length: 5 }).map((_, index) => (
        <button
          key={index}
          type="button"
          className={`tile ${COLOR_CLASS[pattern[index] ?? 0]}`}
          title={`Click to cycle color (${COLOR_LABEL[pattern[index] ?? 0]})`}
          onClick={() => cycleColor(index)}
          disabled={!editable}
        >
          <input
            className="tile-input"
            maxLength={1}
            value={word[index] ?? ""}
            disabled={!editable}
            style={{ pointerEvents: editable ? "auto" : "none" }}
            onChange={(event) => updateLetter(index, event.target.value)}
            onClick={(event) => event.stopPropagation()}
          />
        </button>
      ))}
    </div>
  );
}

type HistoryBoardProps = {
  rows: { word: string; pattern: TileColor[] }[];
};

export function HistoryBoard({ rows }: HistoryBoardProps) {
  return (
    <div className="history">
      {rows.map((row, index) => (
        <Board key={index} word={row.word} pattern={row.pattern} />
      ))}
    </div>
  );
}
