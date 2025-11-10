import { ReactNode } from 'react';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="layout-header">
        <h1>CICS PA Monitor</h1>
        <p className="subtitle">Monitoreo de Abends en Regiones CICS</p>
      </header>
      <main className="layout-main">{children}</main>
      <footer className="layout-footer">
        <p>CICS Performance Analyzer Backend v1.0.0</p>
      </footer>
    </div>
  );
}
