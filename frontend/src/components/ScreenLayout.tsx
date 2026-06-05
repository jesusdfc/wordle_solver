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
      </div>
    </main>
  );
}
