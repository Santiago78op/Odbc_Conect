"""
Aplicación principal FastAPI.
Punto de entrada del backend de monitoreo de abends CICS PA.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from .core import get_settings, get_logger
from .core.metrics import initialize_metrics
from .core.middleware import (
    PrometheusMetricsMiddleware,
    SystemMetricsMiddleware,
    RequestLoggingMiddleware
)
from .database import get_odbc_manager
from .api import health, tables, query, metrics

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    - Startup: Inicializa conexiones
    - Shutdown: Cierra conexiones
    """
    # Startup
    logger.info("=== Iniciando CICS PA Backend ===")
    settings = get_settings()

    try:
        # Inicializar métricas de Prometheus
        logger.info("Inicializando métricas de Prometheus...")
        initialize_metrics(settings.app_name, settings.app_version)
        logger.info("Métricas inicializadas correctamente")

        # Inicializar pool de conexiones ODBC
        logger.info("Inicializando pool de conexiones ODBC...")
        odbc_manager = get_odbc_manager()
        logger.info("Pool ODBC inicializado correctamente")

    except Exception as e:
        logger.error(f"Error inicializando aplicación: {e}")
        raise

    logger.info(f"Aplicación iniciada: {settings.app_name} v{settings.app_version}")

    yield

    # Shutdown
    logger.info("=== Cerrando CICS PA Backend ===")
    try:
        odbc_manager = get_odbc_manager()
        odbc_manager.close()
        logger.info("Conexiones cerradas correctamente")
    except Exception as e:
        logger.error(f"Error cerrando conexiones: {e}")


# Crear aplicación FastAPI
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Backend para monitoreo de abends en regiones CICS.

    Conecta a DVM por ODBC y proporciona endpoints REST para:
    - Consultar abends por región y programa
    - Ejecutar queries personalizadas
    - Obtener información de tablas
    - Generar reportes y estadísticas

    **CICS Performance Analyzer (CICS PA)** es una herramienta de análisis de performance
    que ayuda a monitorear y gestionar sistemas CICS Transaction Server.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Prometheus (primero para capturar todas las requests)
app.add_middleware(PrometheusMetricsMiddleware)

# Middleware de métricas del sistema
app.add_middleware(SystemMetricsMiddleware)

# Middleware de logging detallado
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para excepciones no manejadas.
    """
    logger.error(f"Error no manejado: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de todas las requests.
    """
    start_time = datetime.utcnow()

    # Log de request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Procesar request
    response = await call_next(request)

    # Log de response
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.2f}ms"
    )

    return response


# Registrar routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(tables.router, prefix=settings.api_prefix)
app.include_router(query.router, prefix=settings.api_prefix)

# Endpoint de métricas (sin prefijo para que sea accesible en /metrics)
app.include_router(metrics.router)


# Root endpoint
@app.get("/")
async def root():
    """
    Endpoint raíz con información de la API.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_prefix}/health",
        "timestamp": datetime.utcnow().isoformat()
    }


# Ejecutar con uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
