"""
Servicio de queries - Lógica de negocio para operaciones de base de datos.
Capa intermedia entre los endpoints y el gestor de ODBC.
"""
import time
from typing import List, Dict, Any, Optional

from ..database import get_odbc_manager
from ..core import get_logger
from ..models import (
    QueryResponse,
    TableInfoResponse,
    ColumnInfo,
    AbendsResponse,
)

logger = get_logger(__name__)


class QueryService:
    """
    Servicio para operaciones de consulta a la base de datos.
    Encapsula la lógica de negocio y manejo de errores.
    """

    def __init__(self):
        self.odbc_manager = get_odbc_manager()

    async def execute_custom_query(
        self,
        query: str,
        params: Optional[List[Any]] = None,
        fetch_all: bool = True
    ) -> QueryResponse:
        """
        Ejecuta una query personalizada.

        Args:
            query: SQL query
            params: Parámetros de la query
            fetch_all: Si traer todos los resultados

        Returns:
            QueryResponse con los resultados
        """
        try:
            start_time = time.time()

            # Convertir params a tuple si existe
            params_tuple = tuple(params) if params else None

            # Ejecutar query
            data = self.odbc_manager.execute_query(
                query=query,
                params=params_tuple,
                fetch_all=fetch_all
            )

            execution_time = (time.time() - start_time) * 1000  # ms

            logger.info(f"Query ejecutada: {len(data)} registros en {execution_time:.2f}ms")

            return QueryResponse(
                success=True,
                data=data,
                row_count=len(data),
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            raise

    async def get_table_info(self, table_name: str) -> TableInfoResponse:
        """
        Obtiene información de una tabla.

        Args:
            table_name: Nombre de la tabla

        Returns:
            TableInfoResponse con la información
        """
        try:
            logger.info(f"Obteniendo información de tabla: {table_name}")

            columns_data = self.odbc_manager.get_table_columns(table_name)

            # Convertir a modelos Pydantic
            columns = [
                ColumnInfo(
                    name=col["name"],
                    type=col["type"],
                    size=col.get("size"),
                    nullable=col["nullable"]
                )
                for col in columns_data
            ]

            return TableInfoResponse(
                table_name=table_name,
                columns=columns,
                total_columns=len(columns)
            )

        except Exception as e:
            logger.error(f"Error obteniendo información de tabla: {e}")
            raise

    async def get_abends(
        self,
        region: Optional[str] = None,
        program: Optional[str] = None,
        limit: int = 100
    ) -> AbendsResponse:
        """
        Obtiene abends filtrados.

        Args:
            region: Región CICS
            program: Nombre del programa
            limit: Límite de registros

        Returns:
            AbendsResponse con los abends
        """
        try:
            logger.info(f"Obteniendo abends: region={region}, program={program}, limit={limit}")

            abends = self.odbc_manager.get_abends(
                region=region,
                program=program,
                limit=limit
            )

            return AbendsResponse(
                success=True,
                abends=abends,
                total=len(abends),
                filters_applied={
                    "region": region,
                    "program": program,
                    "limit": limit
                }
            )

        except Exception as e:
            logger.error(f"Error obteniendo abends: {e}")
            raise

    async def get_abends_summary(
        self,
        region: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Obtiene resumen estadístico de abends.

        Args:
            region: Región CICS
            limit: Límite de registros a analizar

        Returns:
            Diccionario con estadísticas
        """
        try:
            logger.info(f"Generando resumen de abends: region={region}")

            abends = self.odbc_manager.get_abends(
                region=region,
                limit=limit
            )

            # Calcular estadísticas
            total = len(abends)
            by_region = {}
            by_program = {}
            by_abend_code = {}

            for abend in abends:
                # Por región
                reg = abend.get('CICS_REGION', 'UNKNOWN')
                by_region[reg] = by_region.get(reg, 0) + 1

                # Por programa
                prog = abend.get('PROGRAM_NAME', 'UNKNOWN')
                by_program[prog] = by_program.get(prog, 0) + 1

                # Por código de abend
                code = abend.get('ABEND_CODE', 'UNKNOWN')
                by_abend_code[code] = by_abend_code.get(code, 0) + 1

            # Top 10 de cada categoría
            summary = {
                "total_abends": total,
                "top_regions": dict(sorted(by_region.items(), key=lambda x: x[1], reverse=True)[:10]),
                "top_programs": dict(sorted(by_program.items(), key=lambda x: x[1], reverse=True)[:10]),
                "top_abend_codes": dict(sorted(by_abend_code.items(), key=lambda x: x[1], reverse=True)[:10]),
                "unique_regions": len(by_region),
                "unique_programs": len(by_program),
                "unique_abend_codes": len(by_abend_code),
            }

            logger.info(f"Resumen generado: {total} abends analizados")
            return summary

        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            raise

    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión a la base de datos.

        Returns:
            Diccionario con el resultado
        """
        try:
            logger.info("Probando conexión a base de datos")

            # Intentar ejecutar una query simple
            result = self.odbc_manager.execute_query(
                query="SELECT 1 AS test",
                fetch_all=True
            )

            connected = len(result) > 0 and result[0].get('test') == 1

            return {
                "connected": connected,
                "message": "Conexión exitosa" if connected else "Conexión fallida"
            }

        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return {
                "connected": False,
                "message": f"Error: {str(e)}"
            }


# Instancia global del servicio
_query_service: Optional[QueryService] = None


def get_query_service() -> QueryService:
    """
    Obtiene la instancia global del QueryService.
    Patrón singleton.
    """
    global _query_service

    if _query_service is None:
        _query_service = QueryService()

    return _query_service
