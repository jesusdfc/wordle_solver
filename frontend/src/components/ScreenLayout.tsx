import type { ReactNode } from "react";

type ScreenLayoutProps = {
  title: string;
  subtitle?: ReactNode;
  badge?: string;
  onBack?: () => void;
  children: ReactNode;
};

export function ScreenLayout({ title, subtitle, badge, onBack, children }: ScreenLayoutProps) {
  return (
    <main className="app">
      <div className="app-card">
        {onBack && (
          <button type="button" className="back-btn" onClick={onBack}>
            ← Menú
          </button>
        )}

        <header className="header">
          <div className="logo" aria-hidden="true">
            P
          </div>
          <h1>{title}</h1>
          {subtitle && <p className="subtitle">{subtitle}</p>}
          {badge && <p className="strategy-badge">{badge}</p>}
        </header>

        {children}

        <footer className="site-footer">
          Hecho por{" "}
          <a
            href="https://github.com/jesusdfc/wordle_solver"
            target="_blank"
            rel="noopener noreferrer"
          >
            Jesús de la Fuente Cedeño
          </a>
        </footer>
      </div>
    </main>
  );
}
