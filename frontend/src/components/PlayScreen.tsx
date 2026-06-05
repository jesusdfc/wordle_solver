import { useState } from "react";

import { fetchSuggestion } from "../api/client";
import type { HistoryRow, TileColor } from "../types";
import { Board, HistoryBoard } from "./Board";
import { ScreenLayout } from "./ScreenLayout";

const EMPTY_PATTERN: TileColor[] = [0, 0, 0, 0, 0];
const MAX_GUESSES = 6;

type PlayScreenProps = {
  onBack: () => void;
};

export function PlayScreen({ onBack }: PlayScreenProps) {
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [currentWord, setCurrentWord] = useState("");
  const [currentPattern, setCurrentPattern] = useState<TileColor[]>([...EMPTY_PATTERN]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<string[] | null>(null);
  const [solved, setSolved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetCurrent = (word = "") => {
    setCurrentWord(word);
    setCurrentPattern([...EMPTY_PATTERN]);
  };

  const handleSuggest = async () => {
    if (history.length >= MAX_GUESSES) return;

    setLoading(true);
    setError(null);

    const nextHistory =
      currentWord.length === 5
        ? [...history, { word: currentWord.toLowerCase(), pattern: currentPattern }]
        : history;

    if (currentWord.length === 5) {
      setHistory(nextHistory);
    }

    if (nextHistory.length >= MAX_GUESSES) {
      setLoading(false);
      return;
    }

    try {
      const result = await fetchSuggestion(nextHistory);
      resetCurrent(result.suggestion);
      setRemaining(result.remaining);
      setCandidates(result.candidates);
      setSolved(result.solved);
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
    setSolved(false);
    setError(null);
  };

  const guessNumber = history.length + (currentWord ? 1 : 0);
  const gameOver = history.length >= MAX_GUESSES || (solved && remaining === 1);

  return (
    <ScreenLayout
      title="Play"
      subtitle={
        <>
          Marca los colores de tu jugada real, luego pulsa <strong>Sugerir</strong> para la
          siguiente palabra.
        </>
      }
      badge="entropy"
      onBack={onBack}
    >
      <section className="board-section">
        <HistoryBoard rows={history} />

        {history.length < MAX_GUESSES && currentWord && (
          <div className="current-row">
            <p className="row-label">Sugerencia actual</p>
            <Board
              word={currentWord}
              pattern={currentPattern}
              interactive
              onPatternChange={setCurrentPattern}
            />
          </div>
        )}

        {history.length < MAX_GUESSES && !currentWord && !loading && (
          <div className="empty-board" aria-hidden="true">
            <div className="board-row">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="tile tile-empty" />
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="color-legend">
        <span className="legend-item">
          <span className="legend-swatch tile-gray" /> Gris
        </span>
        <span className="legend-item">
          <span className="legend-swatch tile-yellow" /> Amarillo
        </span>
        <span className="legend-item">
          <span className="legend-swatch tile-green" /> Verde
        </span>
      </section>

      <section className="actions">
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSuggest}
          disabled={loading || gameOver}
        >
          {loading ? "Calculando…" : currentWord ? "Sugerir siguiente" : "Sugerir"}
        </button>
        <button type="button" className="btn btn-secondary" onClick={handleReset} disabled={loading}>
          Reiniciar
        </button>
      </section>

      <section className="status-panel">
        {remaining !== null && (
          <p className="stats">
            <span className="stats-value">{remaining.toLocaleString()}</span>
            <span className="stats-label">palabras posibles</span>
          </p>
        )}
        {guessNumber > 0 && (
          <p className="guess-count">
            Intento {Math.min(guessNumber, MAX_GUESSES)} / {MAX_GUESSES}
          </p>
        )}
        {solved && remaining === 1 && candidates?.[0] && (
          <p className="solved-banner">¡Resuelto! La palabra es {candidates[0].toUpperCase()}</p>
        )}
        {candidates && candidates.length > 1 && (
          <details className="candidates-details">
            <summary>Candidatos ({candidates.length})</summary>
            <p className="candidates">{candidates.join(", ")}</p>
          </details>
        )}
        {error && <p className="error">{error}</p>}
      </section>
    </ScreenLayout>
  );
}
