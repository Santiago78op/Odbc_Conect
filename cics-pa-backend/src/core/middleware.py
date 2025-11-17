"""
Middleware personalizado para la aplicación.

Este módulo contiene middleware para captura de métricas,
logging y observabilidad siguiendo PEP 8.
"""
import time
import sys
from typing import Callable
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .metrics import (
    http_requests_in_progress,
    record_http_request,
    record_exception,
    application_memory_usage_bytes,
    application_cpu_usage_percent
)
from .logging import get_logger

logger = get_logger(__name__)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para capturar métricas de Prometheus automáticamente.

    Captura métricas de:
    - Duración de requests
    - Tamaño de requests y responses
    - Códigos de estado
    - Requests en progreso
    - Excepciones
    """

    def __init__(self, app: ASGIApp):
        """
        Inicializa el middleware.

        Args:
            app: Aplicación ASGI
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Procesa cada request y captura métricas.

        Args:
            request: Request HTTP
            call_next: Siguiente middleware en la cadena

        Returns:
            Response HTTP
        """
        # Extraer información del request
        method = request.method
        endpoint = self._get_endpoint_path(request)

        # Incrementar contador de requests en progreso
        http_requests_in_progress.labels(
            method=method,
            endpoint=endpoint
        ).inc()

        # Medir tamaño del request si está disponible
        request_size = None
        if 'content-length' in request.headers:
            try:
                request_size = int(request.headers['content-length'])
            except (ValueError, TypeError):
                pass

        # Iniciar temporizador
        start_time = time.perf_counter()

        try:
            # Procesar request
            response = await call_next(request)

            # Calcular duración
            duration = time.perf_counter() - start_time

            # Obtener tamaño de response
            response_size = None
            if hasattr(response, 'headers') and 'content-length' in response.headers:
                try:
                    response_size = int(response.headers['content-length'])
                except (ValueError, TypeError):
                    pass

            # Registrar métricas
            record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
                request_size=request_size,
                response_size=response_size
            )

            return response

        except Exception as exc:
            # Registrar excepción
            duration = time.perf_counter() - start_time
            exception_type = type(exc).__name__

            record_exception(
                exception_type=exception_type,
                endpoint=endpoint
            )

            # Registrar request con error
            record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration,
                request_size=request_size
            )

            # Re-lanzar la excepción para que la maneje el handler global
            raise

        finally:
            # Decrementar contador de requests en progreso
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint
            ).dec()

    @staticmethod
    def _get_endpoint_path(request: Request) -> str:
        """
        Obtiene el path del endpoint normalizado.

        Args:
            request: Request HTTP

        Returns:
            Path del endpoint
        """
        # Si hay una ruta coincidente, usar el patrón de la ruta
        if request.url.path == '/metrics':
            return '/metrics'

        # Intentar obtener el path pattern de la ruta
        if hasattr(request, 'scope') and 'route' in request.scope:
            route = request.scope['route']
            if hasattr(route, 'path'):
                return route.path

        # Si no hay patrón, usar el path completo
        return request.url.path


class SystemMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para capturar métricas del sistema.

    Captura métricas de:
    - Uso de memoria
    - Uso de CPU
    """

    def __init__(self, app: ASGIApp):
        """
        Inicializa el middleware.

        Args:
            app: Aplicación ASGI
        """
        super().__init__(app)
        self._last_update = 0
        self._update_interval = 5  # Actualizar cada 5 segundos

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Procesa cada request y actualiza métricas del sistema.

        Args:
            request: Request HTTP
            call_next: Siguiente middleware en la cadena

        Returns:
            Response HTTP
        """
        # Actualizar métricas del sistema periódicamente
        current_time = time.time()
        if current_time - self._last_update >= self._update_interval:
            self._update_system_metrics()
            self._last_update = current_time

        # Continuar con el request
        response = await call_next(request)
        return response

    @staticmethod
    def _update_system_metrics() -> None:
        """
        Actualiza las métricas del sistema (CPU y memoria).
        """
        try:
            import psutil
            import os

            # Obtener proceso actual
            process = psutil.Process(os.getpid())

            # Actualizar memoria
            memory_info = process.memory_info()
            application_memory_usage_bytes.set(memory_info.rss)

            # Actualizar CPU
            cpu_percent = process.cpu_percent(interval=None)
            application_cpu_usage_percent.set(cpu_percent)

        except ImportError:
            # psutil no está instalado, no actualizar métricas
            pass
        except Exception as e:
            logger.error(f"Error actualizando métricas del sistema: {e}")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging detallado de requests.

    Complementa el logging básico con información adicional útil
    para debugging y auditoría.
    """

    def __init__(self, app: ASGIApp):
        """
        Inicializa el middleware.

        Args:
            app: Aplicación ASGI
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Procesa cada request y genera logs detallados.

        Args:
            request: Request HTTP
            call_next: Siguiente middleware en la cadena

        Returns:
            Response HTTP
        """
        # Información del request
        request_id = id(request)
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"

        # Log de inicio
        logger.debug(
            f"[{request_id}] Request iniciado: {method} {path} "
            f"from {client_host}"
        )

        # Iniciar temporizador
        start_time = time.perf_counter()

        try:
            # Procesar request
            response = await call_next(request)

            # Calcular duración
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log de finalización
            logger.info(
                f"[{request_id}] Request completado: {method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration_ms:.2f}ms"
            )

            return response

        except Exception as exc:
            # Calcular duración
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log de error
            logger.error(
                f"[{request_id}] Request fallido: {method} {path} - "
                f"Error: {type(exc).__name__} - "
                f"Duration: {duration_ms:.2f}ms",
                exc_info=True
            )

            # Re-lanzar la excepción
            raise


# ============================================================================
# Exportar middleware
# ============================================================================

__all__ = [
    'PrometheusMetricsMiddleware',
    'SystemMetricsMiddleware',
    'RequestLoggingMiddleware',
]
