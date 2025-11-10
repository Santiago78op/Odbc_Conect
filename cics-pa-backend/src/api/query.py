"""
Endpoints para ejecución de queries.
Permite ejecutar consultas personalizadas y obtener abends.
"""
from fastapi import APIRouter, Depends, HTTPException, Query

from ..models import (
    QueryRequest,
    QueryResponse,
    AbendsFilterRequest,
    AbendsResponse,
)
from ..services import get_query_service, QueryService
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Ejecuta una query SQL personalizada.

    **Restricciones de seguridad:**
    - No se permiten queries DDL (DROP, CREATE, ALTER, etc.)
    - Solo queries de lectura (SELECT)

    Args:
        request: QueryRequest con la query y parámetros

    Returns:
        QueryResponse con los resultados

    Raises:
        HTTPException: Si hay error ejecutando la query
    """
    try:
        logger.info(f"Endpoint /query/execute - query: {request.query[:100]}...")

        result = await service.execute_custom_query(
            query=request.query,
            params=request.params,
            fetch_all=request.fetch_all
        )

        return result

    except ValueError as e:
        # Error de validación
        logger.warning(f"Validación fallida en /query/execute: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error en /query/execute: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando query: {str(e)}"
        )


@router.post("/abends", response_model=AbendsResponse)
async def get_abends(
    request: AbendsFilterRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Obtiene abends de CICS PA con filtros opcionales.

    Args:
        request: AbendsFilterRequest con filtros

    Returns:
        AbendsResponse con los abends encontrados

    Raises:
        HTTPException: Si hay error obteniendo abends
    """
    try:
        logger.info(f"Endpoint /query/abends - filtros: {request.dict()}")

        result = await service.get_abends(
            region=request.region,
            program=request.program,
            limit=request.limit
        )

        return result

    except Exception as e:
        logger.error(f"Error en /query/abends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo abends: {str(e)}"
        )


@router.get("/abends", response_model=AbendsResponse)
async def get_abends_by_params(
    region: str = Query(None, description="Región CICS"),
    program: str = Query(None, description="Nombre del programa"),
    limit: int = Query(100, description="Límite de registros", ge=1, le=1000),
    service: QueryService = Depends(get_query_service)
):
    """
    Obtiene abends de CICS PA con query parameters.

    Args:
        region: Región CICS (opcional)
        program: Nombre del programa (opcional)
        limit: Límite de registros (1-1000)

    Returns:
        AbendsResponse con los abends encontrados

    Raises:
        HTTPException: Si hay error obteniendo abends
    """
    try:
        logger.info(f"Endpoint GET /query/abends - region={region}, program={program}, limit={limit}")

        result = await service.get_abends(
            region=region,
            program=program,
            limit=limit
        )

        return result

    except Exception as e:
        logger.error(f"Error en GET /query/abends: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo abends: {str(e)}"
        )


@router.get("/abends/summary")
async def get_abends_summary(
    region: str = Query(None, description="Región CICS"),
    limit: int = Query(1000, description="Límite de registros a analizar", ge=1, le=10000),
    service: QueryService = Depends(get_query_service)
):
    """
    Obtiene resumen estadístico de abends.

    Proporciona:
    - Total de abends
    - Top 10 regiones con más abends
    - Top 10 programas con más abends
    - Top 10 códigos de abend más frecuentes
    - Totales únicos

    Args:
        region: Región CICS (opcional)
        limit: Límite de registros a analizar

    Returns:
        Diccionario con estadísticas

    Raises:
        HTTPException: Si hay error generando resumen
    """
    try:
        logger.info(f"Endpoint /query/abends/summary - region={region}, limit={limit}")

        result = await service.get_abends_summary(
            region=region,
            limit=limit
        )

        return {
            "success": True,
            "summary": result
        }

    except Exception as e:
        logger.error(f"Error en /query/abends/summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando resumen: {str(e)}"
        )
