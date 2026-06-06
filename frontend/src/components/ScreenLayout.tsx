import type { ReactNode } from "react";

const REPO_URL = "https://github.com/jesusdfc/wordle_solver";
const PERSONAL_SITE_URL = "https://jesusdfc.github.io/";

function GitHubIcon() {
  return (
    <svg
      className="github-icon"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <path
        fill="currentColor"
        d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"
      />
    </svg>
  );
}

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
          <a
            className="site-footer-contribute"
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            <span>Want to contribute?</span>
            <GitHubIcon />
          </a>

          <div className="site-footer-credit">
            <span className="site-footer-label">Hecho por:</span>
            <span className="site-footer-name">Jesús de la Fuente Cedeño</span>
            <a
              className="site-footer-site"
              href={PERSONAL_SITE_URL}
              target="_blank"
              rel="noopener noreferrer"
            >
              jesusdfc.github.io
            </a>
          </div>
        </footer>
      </div>
    </main>
  );
}
