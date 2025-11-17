"""
Endpoint para métricas de Prometheus.

Este módulo expone el endpoint /metrics que Prometheus
utiliza para recopilar métricas de la aplicación.
"""
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=['metrics'])


@router.get('/metrics')
async def metrics() -> Response:
    """
    Endpoint de métricas para Prometheus.

    Retorna todas las métricas en formato Prometheus.

    Returns:
        Response con métricas en formato Prometheus
    """
    metrics_output = generate_latest()

    return Response(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST,
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    )
