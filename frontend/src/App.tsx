import { useState } from "react";

import { fetchSuggestion } from "./api/client";
import { Board, HistoryBoard } from "./components/Board";
import type { HistoryRow, TileColor } from "./types";

const EMPTY_PATTERN: TileColor[] = [0, 0, 0, 0, 0];

export default function App() {
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [currentWord, setCurrentWord] = useState("");
  const [currentPattern, setCurrentPattern] = useState<TileColor[]>([...EMPTY_PATTERN]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strategy, setStrategy] = useState("entropy");

  const resetCurrent = (word = "") => {
    setCurrentWord(word);
    setCurrentPattern([...EMPTY_PATTERN]);
  };

  const handleSuggest = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchSuggestion(history, strategy);
      resetCurrent(result.suggestion);
      setRemaining(result.remaining);
      setCandidates(result.candidates);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (currentWord.length !== 5) {
      setError("Enter a 5-letter word before confirming.");
      return;
    }

    const nextHistory = [...history, { word: currentWord.toLowerCase(), pattern: currentPattern }];
    setHistory(nextHistory);
    setLoading(true);
    setError(null);

    try {
      const result = await fetchSuggestion(nextHistory, strategy);
      resetCurrent(result.suggestion);
      setRemaining(result.remaining);
      setCandidates(result.candidates);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setHistory([]);
    resetCurrent();
    setRemaining(null);
    setCandidates(null);
    setError(null);
  };

  return (
    <main className="app">
      <header>
        <h1>Palabra Solver</h1>
        <p>Mark each letter gray / yellow / green, then confirm or ask for a suggestion.</p>
      </header>

      <section className="controls">
        <label>
          Strategy
          <select value={strategy} onChange={(event) => setStrategy(event.target.value)}>
            <option value="entropy">entropy</option>
            <option value="minimax">minimax</option>
          </select>
        </label>
      </section>

      <HistoryBoard rows={history} />

      {history.length < 6 && (
        <section className="current-row">
          <h2>Current guess</h2>
          <Board
            word={currentWord}
            pattern={currentPattern}
            editable
            onWordChange={setCurrentWord}
            onPatternChange={setCurrentPattern}
          />
        </section>
      )}

      <section className="actions">
        <button type="button" onClick={handleSuggest} disabled={loading || history.length >= 6}>
          {loading ? "Thinking…" : "Suggest"}
        </button>
        <button type="button" onClick={handleConfirm} disabled={loading || history.length >= 6}>
          Confirm row
        </button>
        <button type="button" onClick={handleReset} disabled={loading}>
          Reset
        </button>
      </section>

      {remaining !== null && <p className="stats">{remaining} words remaining</p>}
      {candidates && (
        <p className="candidates">Candidates: {candidates.join(", ")}</p>
      )}
      {error && <p className="error">{error}</p>}

      <footer>
        <p>Click a tile to cycle color. Type the word you played in the real game.</p>
      </footer>
    </main>
  );
}
