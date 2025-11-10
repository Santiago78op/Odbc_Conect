"""
Endpoint de health check.
Verifica el estado del servicio y la conexión a la base de datos.
"""
from fastapi import APIRouter, Depends
from datetime import datetime

from ..models import HealthResponse
from ..core import get_settings
from ..services import get_query_service, QueryService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check(
    service: QueryService = Depends(get_query_service)
):
    """
    Health check endpoint.

    Verifica:
    - Estado del servicio
    - Conexión a base de datos
    - Configuración básica

    Returns:
        HealthResponse con el estado del sistema
    """
    settings = get_settings()

    # Probar conexión a DB
    db_status = await service.test_connection()

    return HealthResponse(
        status="healthy" if db_status["connected"] else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database_connected=db_status["connected"],
        details={
            "app_name": settings.app_name,
            "odbc_dsn": settings.odbc_dsn,
            "pool_size": settings.pool_size,
            "db_message": db_status["message"]
        }
    )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint.

    Returns:
        Mensaje de pong
    """
    return {"message": "pong", "timestamp": datetime.utcnow()}
