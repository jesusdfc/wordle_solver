import { ScreenLayout } from "./ScreenLayout";

type MenuScreenProps = {
  onPlay: () => void;
  onBenchmark: () => void;
};

export function MenuScreen({ onPlay, onBenchmark }: MenuScreenProps) {
  return (
    <ScreenLayout
      title="Spanish Wordle Solver"
      subtitle={
        <>
          Asistente óptimo para <strong>La Palabra del Día</strong>. Elige un modo para empezar.
        </>
      }
      badge="entropy"
    >
      <nav className="menu-actions" aria-label="Modos">
        <button type="button" className="menu-btn menu-btn-play" onClick={onPlay}>
          <span className="menu-btn-icon" aria-hidden="true">
            ▶
          </span>
          <span className="menu-btn-text">
            <strong>Play</strong>
            <small>Marca colores y pide sugerencias en vivo</small>
          </span>
        </button>

        <button type="button" className="menu-btn menu-btn-benchmark" onClick={onBenchmark}>
          <span className="menu-btn-icon" aria-hidden="true">
            ◷
          </span>
          <span className="menu-btn-text">
            <strong>Benchmark</strong>
            <small>Simula la ruta del solver contra un secreto</small>
          </span>
        </button>
      </nav>
    </ScreenLayout>
  );
}
