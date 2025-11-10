import { AbendsTable } from '../components/AbendsTable/AbendsTable';
import { useHealth } from '../hooks/useApi';
import './Dashboard.css';

export function Dashboard() {
  const { data: health } = useHealth();

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="status-indicator">
          <span
            className={`status-dot ${health?.database_connected ? 'online' : 'offline'}`}
          ></span>
          <span className="status-text">
            {health?.database_connected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
        <div className="version-info">
          <span>Backend v{health?.version || '...'}</span>
        </div>
      </div>

      <AbendsTable />
    </div>
  );
}
