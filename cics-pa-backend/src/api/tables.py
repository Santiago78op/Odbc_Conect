"""
Endpoints para gestión de tablas.
Obtiene información sobre tablas y columnas.
"""
from fastapi import APIRouter, Depends, HTTPException

from ..models import TableInfoRequest, TableInfoResponse
from ..services import get_query_service, QueryService
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/tables", tags=["Tables"])


@router.post("/info", response_model=TableInfoResponse)
async def get_table_info(
    request: TableInfoRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Obtiene información de una tabla.

    Args:
        request: TableInfoRequest con el nombre de la tabla

    Returns:
        TableInfoResponse con columnas y metadata

    Raises:
        HTTPException: Si hay error obteniendo la información
    """
    try:
        logger.info(f"Endpoint /tables/info - tabla: {request.table_name}")

        result = await service.get_table_info(request.table_name)

        return result

    except Exception as e:
        logger.error(f"Error en /tables/info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de tabla: {str(e)}"
        )


@router.get("/info/{table_name}", response_model=TableInfoResponse)
async def get_table_info_by_path(
    table_name: str,
    service: QueryService = Depends(get_query_service)
):
    """
    Obtiene información de una tabla (por path parameter).

    Args:
        table_name: Nombre de la tabla

    Returns:
        TableInfoResponse con columnas y metadata

    Raises:
        HTTPException: Si hay error obteniendo la información
    """
    try:
        logger.info(f"Endpoint GET /tables/info/{table_name}")

        result = await service.get_table_info(table_name)

        return result

    except Exception as e:
        logger.error(f"Error en GET /tables/info/{table_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de tabla: {str(e)}"
        )
