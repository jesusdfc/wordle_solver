import { ScreenLayout } from "./ScreenLayout";

type MenuScreenProps = {
  onPlay: () => void;
  onExplore: () => void;
};

export function MenuScreen({ onPlay, onExplore }: MenuScreenProps) {
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

        <button type="button" className="menu-btn menu-btn-explore" onClick={onExplore}>
          <span className="menu-btn-icon" aria-hidden="true">
            ◷
          </span>
          <span className="menu-btn-text">
            <strong>Explore</strong>
            <small>Simula la ruta del solver contra un secreto</small>
          </span>
        </button>
      </nav>
    </ScreenLayout>
  );
}
