import { Link } from "react-router-dom";

import { ScreenLayout } from "./ScreenLayout";

export function MenuScreen() {
  return (
    <ScreenLayout
      title="Spanish Wordle Solver"
      subtitle={
        <>
          Asistente óptimo para <strong>La Palabra del Día</strong>. Elige un modo para empezar.
        </>
      }
    >
      <nav className="menu-actions" aria-label="Modos">
        <Link to="/play" className="menu-btn menu-btn-play">
          <span className="menu-btn-icon" aria-hidden="true">
            ▶
          </span>
          <span className="menu-btn-text">
            <strong>Play</strong>
            <small>Marca colores y pide sugerencias en vivo</small>
          </span>
        </Link>

        <Link to="/explore" className="menu-btn menu-btn-explore">
          <span className="menu-btn-icon" aria-hidden="true">
            ◷
          </span>
          <span className="menu-btn-text">
            <strong>Explore</strong>
            <small>Simula la ruta del solver contra un secreto</small>
          </span>
        </Link>
      </nav>
    </ScreenLayout>
  );
}
