import './ErrorMessage.css';

interface ErrorMessageProps {
  message: string;
  details?: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, details, onRetry }: ErrorMessageProps) {
  return (
    <div className="error-container">
      <div className="error-icon">⚠️</div>
      <h3 className="error-title">Error</h3>
      <p className="error-message">{message}</p>
      {details && <p className="error-details">{details}</p>}
      {onRetry && (
        <button className="error-retry-btn" onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  );
}
