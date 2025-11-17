"""
Módulo de métricas de Prometheus.

Este módulo centraliza todas las métricas de la aplicación siguiendo
las mejores prácticas de observabilidad y PEP 8.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Optional


# ============================================================================
# Métricas de aplicación
# ============================================================================

app_info = Info(
    'cics_pa_application',
    'Información de la aplicación CICS PA Backend'
)

# ============================================================================
# Métricas HTTP
# ============================================================================

http_requests_total = Counter(
    'cics_pa_http_requests_total',
    'Total de requests HTTP recibidas',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'cics_pa_http_request_duration_seconds',
    'Duración de las requests HTTP en segundos',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

http_request_size_bytes = Histogram(
    'cics_pa_http_request_size_bytes',
    'Tamaño de las requests HTTP en bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'cics_pa_http_response_size_bytes',
    'Tamaño de las responses HTTP en bytes',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'cics_pa_http_requests_in_progress',
    'Número de requests HTTP en progreso',
    ['method', 'endpoint']
)

# ============================================================================
# Métricas de ODBC/Base de datos
# ============================================================================

db_connections_active = Gauge(
    'cics_pa_db_connections_active',
    'Número de conexiones ODBC activas en el pool'
)

db_connections_total = Counter(
    'cics_pa_db_connections_total',
    'Total de conexiones ODBC creadas',
    ['status']  # success, error
)

db_query_duration_seconds = Histogram(
    'cics_pa_db_query_duration_seconds',
    'Duración de queries ODBC en segundos',
    ['operation', 'table'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

db_queries_total = Counter(
    'cics_pa_db_queries_total',
    'Total de queries ODBC ejecutadas',
    ['operation', 'table', 'status']  # operation: select, insert, etc.
)

db_connection_errors_total = Counter(
    'cics_pa_db_connection_errors_total',
    'Total de errores de conexión ODBC',
    ['error_type']
)

db_query_errors_total = Counter(
    'cics_pa_db_query_errors_total',
    'Total de errores en queries ODBC',
    ['operation', 'error_type']
)

# ============================================================================
# Métricas de negocio - CICS Abends
# ============================================================================

cics_abends_total = Counter(
    'cics_pa_abends_total',
    'Total de abends detectados en CICS',
    ['region', 'program', 'abend_code']
)

cics_abends_query_total = Counter(
    'cics_pa_abends_query_total',
    'Total de consultas de abends realizadas',
    ['region', 'status']
)

cics_regions_monitored = Gauge(
    'cics_pa_regions_monitored',
    'Número de regiones CICS actualmente monitoreadas'
)

# ============================================================================
# Métricas de rendimiento de la aplicación
# ============================================================================

application_memory_usage_bytes = Gauge(
    'cics_pa_application_memory_usage_bytes',
    'Uso de memoria de la aplicación en bytes'
)

application_cpu_usage_percent = Gauge(
    'cics_pa_application_cpu_usage_percent',
    'Uso de CPU de la aplicación en porcentaje'
)

# ============================================================================
# Métricas de errores
# ============================================================================

application_exceptions_total = Counter(
    'cics_pa_application_exceptions_total',
    'Total de excepciones en la aplicación',
    ['exception_type', 'endpoint']
)

# ============================================================================
# Funciones auxiliares para registro de métricas
# ============================================================================


def record_http_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    request_size: Optional[int] = None,
    response_size: Optional[int] = None
) -> None:
    """
    Registra métricas de una request HTTP.

    Args:
        method: Método HTTP (GET, POST, etc.)
        endpoint: Path del endpoint
        status_code: Código de estado HTTP
        duration: Duración de la request en segundos
        request_size: Tamaño de la request en bytes (opcional)
        response_size: Tamaño de la response en bytes (opcional)
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

    if request_size is not None:
        http_request_size_bytes.labels(
            method=method,
            endpoint=endpoint
        ).observe(request_size)

    if response_size is not None:
        http_response_size_bytes.labels(
            method=method,
            endpoint=endpoint
        ).observe(response_size)


def record_db_query(
    operation: str,
    table: str,
    duration: float,
    status: str = 'success',
    error_type: Optional[str] = None
) -> None:
    """
    Registra métricas de una query a la base de datos.

    Args:
        operation: Tipo de operación (SELECT, INSERT, etc.)
        table: Nombre de la tabla
        duration: Duración de la query en segundos
        status: Estado de la query (success, error)
        error_type: Tipo de error si status='error' (opcional)
    """
    db_queries_total.labels(
        operation=operation,
        table=table,
        status=status
    ).inc()

    db_query_duration_seconds.labels(
        operation=operation,
        table=table
    ).observe(duration)

    if error_type:
        db_query_errors_total.labels(
            operation=operation,
            error_type=error_type
        ).inc()


def record_cics_abend(
    region: str,
    program: str,
    abend_code: str
) -> None:
    """
    Registra un abend de CICS detectado.

    Args:
        region: Región CICS donde ocurrió el abend
        program: Programa que generó el abend
        abend_code: Código del abend
    """
    cics_abends_total.labels(
        region=region,
        program=program,
        abend_code=abend_code
    ).inc()


def record_exception(
    exception_type: str,
    endpoint: str
) -> None:
    """
    Registra una excepción en la aplicación.

    Args:
        exception_type: Tipo de excepción
        endpoint: Endpoint donde ocurrió la excepción
    """
    application_exceptions_total.labels(
        exception_type=exception_type,
        endpoint=endpoint
    ).inc()


def initialize_metrics(app_name: str, version: str) -> None:
    """
    Inicializa las métricas de información de la aplicación.

    Args:
        app_name: Nombre de la aplicación
        version: Versión de la aplicación
    """
    app_info.info({
        'app_name': app_name,
        'version': version
    })


# ============================================================================
# Exportar métricas y funciones públicas
# ============================================================================

__all__ = [
    # Info
    'app_info',
    'initialize_metrics',
    # HTTP
    'http_requests_total',
    'http_request_duration_seconds',
    'http_request_size_bytes',
    'http_response_size_bytes',
    'http_requests_in_progress',
    'record_http_request',
    # Database
    'db_connections_active',
    'db_connections_total',
    'db_query_duration_seconds',
    'db_queries_total',
    'db_connection_errors_total',
    'db_query_errors_total',
    'record_db_query',
    # CICS Business
    'cics_abends_total',
    'cics_abends_query_total',
    'cics_regions_monitored',
    'record_cics_abend',
    # Application
    'application_memory_usage_bytes',
    'application_cpu_usage_percent',
    'application_exceptions_total',
    'record_exception',
]
