import { useEffect, useState } from "react";

import { fetchStrategies } from "../api/client";
import type { SolverStrategy, StrategyInfo } from "../types";

type StrategySelectorProps = {
  value: SolverStrategy;
  onChange: (strategy: SolverStrategy) => void;
  openingWord: string;
  onOpeningWordChange: (word: string) => void;
  disabled?: boolean;
};

const HIGHLIGHT_LABELS: Record<NonNullable<StrategyInfo["highlight"]>, string> = {
  best: "Best performant",
  fast: "Faster",
};

function optionClassName(option: StrategyInfo, selected: boolean): string {
  const classes = ["strategy-option"];
  if (selected) classes.push("strategy-option-active");
  if (option.highlight === "best") classes.push("strategy-option-highlight-best");
  if (option.highlight === "fast") classes.push("strategy-option-highlight-fast");
  return classes.join(" ");
}

export function StrategySelector({
  value,
  onChange,
  openingWord,
  onOpeningWordChange,
  disabled = false,
}: StrategySelectorProps) {
  const [options, setOptions] = useState<StrategyInfo[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchStrategies()
      .then((items) => {
        if (!cancelled) setOptions(items);
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : "Failed to load strategies");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const selected = options.find((option) => option.id === value) ?? options[0];
  const showOpeningWord = selected?.requires_opening_word ?? false;

  return (
    <section className="strategy-picker" aria-label="Solver strategy">
      <span className="strategy-picker-label">Strategy</span>
      {loadError ? <p className="error-text">{loadError}</p> : null}
      <div className="strategy-picker-options">
        {options.map((option) => {
          const isSelected = value === option.id;
          const highlightLabel = option.highlight ? HIGHLIGHT_LABELS[option.highlight] : null;

          return (
            <label key={option.id} className={optionClassName(option, isSelected)}>
              <input
                type="radio"
                name="solver-strategy"
                value={option.id}
                checked={isSelected}
                disabled={disabled || options.length === 0}
                onChange={() => onChange(option.id)}
              />
              <span className="strategy-option-header">
                <span className="strategy-option-name">{option.label}</span>
                {highlightLabel ? (
                  <span className={`strategy-option-tag strategy-option-tag-${option.highlight}`}>
                    {highlightLabel}
                  </span>
                ) : null}
              </span>
              <span className="strategy-option-hint">{option.description}</span>
            </label>
          );
        })}
      </div>
      {selected?.warning && value === selected.id ? (
        <p className="strategy-warning-banner" role="status">
          {selected.warning}
        </p>
      ) : null}
      {showOpeningWord ? (
        <label className="opening-word-field">
          <span className="strategy-picker-label">Opening word</span>
          <input
            type="text"
            maxLength={5}
            value={openingWord}
            disabled={disabled}
            placeholder={selected?.default_opening_word ?? "cario"}
            onChange={(event) => onOpeningWordChange(event.target.value.toLowerCase())}
          />
        </label>
      ) : null}
    </section>
  );
}
