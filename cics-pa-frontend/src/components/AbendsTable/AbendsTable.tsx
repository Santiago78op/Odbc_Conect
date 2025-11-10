import { useState } from 'react';
import { useAbends } from '../../hooks/useApi';
import { Loading } from '../Loading/Loading';
import { ErrorMessage } from '../ErrorMessage/ErrorMessage';
import type { AbendRecord } from '../../types/api.types';
import './AbendsTable.css';

export function AbendsTable() {
  const [region, setRegion] = useState<string>('');
  const [program, setProgram] = useState<string>('');
  const [limit, setLimit] = useState<number>(100);

  const { data, isLoading, error, refetch } = useAbends(
    {
      region: region || undefined,
      program: program || undefined,
      limit,
    },
    {
      refetchOnMount: true,
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    refetch();
  };

  if (error) {
    return (
      <ErrorMessage
        message="Error al cargar los abends"
        details={error instanceof Error ? error.message : 'Error desconocido'}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="abends-table-container">
      <div className="filters-section">
        <h2>Filtros de Búsqueda</h2>
        <form onSubmit={handleSubmit} className="filters-form">
          <div className="form-group">
            <label htmlFor="region">Región CICS:</label>
            <input
              id="region"
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="Ej: PROD01"
            />
          </div>

          <div className="form-group">
            <label htmlFor="program">Programa:</label>
            <input
              id="program"
              type="text"
              value={program}
              onChange={(e) => setProgram(e.target.value)}
              placeholder="Ej: PAYROLL"
            />
          </div>

          <div className="form-group">
            <label htmlFor="limit">Límite:</label>
            <input
              id="limit"
              type="number"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              min="1"
              max="1000"
            />
          </div>

          <button type="submit" className="search-btn">
            Buscar
          </button>
        </form>
      </div>

      {isLoading ? (
        <Loading message="Cargando abends..." />
      ) : (
        <>
          <div className="results-header">
            <h2>Resultados</h2>
            <span className="results-count">
              Total: {data?.total || 0} abend(s)
            </span>
          </div>

          {data && data.abends.length > 0 ? (
            <div className="table-wrapper">
              <table className="abends-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Región CICS</th>
                    <th>Programa</th>
                    <th>Código Abend</th>
                    <th>Transaction ID</th>
                    <th>User ID</th>
                    <th>Terminal ID</th>
                  </tr>
                </thead>
                <tbody>
                  {data.abends.map((abend: AbendRecord, index: number) => (
                    <tr key={index}>
                      <td>{abend.timestamp || '-'}</td>
                      <td>
                        <span className="badge badge-region">
                          {abend.cics_region || '-'}
                        </span>
                      </td>
                      <td>
                        <code>{abend.program_name || '-'}</code>
                      </td>
                      <td>
                        <span className="badge badge-abend">
                          {abend.abend_code || '-'}
                        </span>
                      </td>
                      <td>{abend.transaction_id || '-'}</td>
                      <td>{abend.user_id || '-'}</td>
                      <td>{abend.terminal_id || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-results">
              <p>No se encontraron abends con los filtros aplicados.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
