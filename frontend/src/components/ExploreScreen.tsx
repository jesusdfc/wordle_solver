import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchExplore } from "../api/client";
import type { ExploreResponse, SolverStrategy } from "../types";
import { Board } from "./Board";
import { ScreenLayout } from "./ScreenLayout";
import { StrategySelector } from "./StrategySelector";

const ROW_REVEAL_MS = 320;

export function ExploreScreen() {
  const navigate = useNavigate();
  const [secretInput, setSecretInput] = useState("");
  const [result, setResult] = useState<ExploreResponse | null>(null);
  const [visibleRows, setVisibleRows] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [animating, setAnimating] = useState(false);
  const [strategy, setStrategy] = useState<SolverStrategy>("entropy-threshold-bellman");
  const [openingWord, setOpeningWord] = useState("cario");

  useEffect(() => {
    if (!result || result.guesses.length === 0) {
      setVisibleRows(0);
      setAnimating(false);
      return;
    }

    setVisibleRows(0);
    setAnimating(true);

    let count = 0;
    const interval = window.setInterval(() => {
      count += 1;
      setVisibleRows(count);
      if (count >= result.guesses.length) {
        window.clearInterval(interval);
        setAnimating(false);
      }
    }, ROW_REVEAL_MS);

    return () => window.clearInterval(interval);
  }, [result]);

  const handleRun = async () => {
    setError(null);
    setResult(null);

    const trimmed = secretInput.trim();
    if (trimmed.length !== 5) {
      setError("5-letter word is expected");
      return;
    }

    setLoading(true);
    try {
      const response = await fetchExplore(trimmed, {
        strategy,
        openingWord: openingWord || undefined,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSecretInput("");
    setResult(null);
    setVisibleRows(0);
    setError(null);
    setAnimating(false);
  };

  const showOutcome = result && !animating && visibleRows >= result.guesses.length;
  const strategyLocked = loading || result !== null;

  return (
    <ScreenLayout
      title="Explore"
      subtitle="Introduce un secreto de 5 letras y observa cómo lo resuelve el solver."
      badge={strategy}
      onBack={() => navigate("/")}
    >
      <StrategySelector
        value={strategy}
        onChange={setStrategy}
        openingWord={openingWord}
        onOpeningWordChange={setOpeningWord}
        disabled={strategyLocked}
      />
      {result && (
        <div className="secret-display">
          <span className="secret-label">Secreto</span>
          <span className="secret-word">{result.secret.toUpperCase()}</span>
        </div>
      )}

      {!result && (
        <section className="explore-input">
          <label className="secret-field-label" htmlFor="secret-input">
            Palabra secreta
          </label>
          <input
            id="secret-input"
            className="secret-input"
            type="text"
            value={secretInput}
            onChange={(event) => setSecretInput(event.target.value)}
            placeholder="ej. abril"
            autoComplete="off"
            spellCheck={false}
            disabled={loading}
          />
        </section>
      )}

      {result && (
        <section className="board-section explore-board">
          <div className="history" aria-label="Ruta del solver">
            {result.guesses.slice(0, visibleRows).map((row, index) => (
              <div key={index} className="board-row-reveal">
                <Board word={row.word} pattern={row.pattern} />
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="actions">
        {!result ? (
          <button type="button" className="btn btn-primary" onClick={handleRun} disabled={loading}>
            {loading ? "Calculando…" : "Explorar"}
          </button>
        ) : (
          <button type="button" className="btn btn-secondary" onClick={handleReset} disabled={animating}>
            Probar otra
          </button>
        )}
      </section>

      <section className="status-panel">
        {result && animating && (
          <p className="guess-count">Reproduciendo ruta… ({visibleRows}/{result.guesses.length})</p>
        )}
        {showOutcome && result.solved && (
          <p className="solved-banner">
            Resuelto en {result.guess_count} {result.guess_count === 1 ? "intento" : "intentos"}
          </p>
        )}
        {showOutcome && !result.solved && (
          <p className="failed-banner">
            No resuelto en {result.guess_count} intentos
          </p>
        )}
        {error && <p className="error">{error}</p>}
      </section>
    </ScreenLayout>
  );
}
