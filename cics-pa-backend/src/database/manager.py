"""
Gestor de conexiones ODBC para DVM.
Maneja el pool de conexiones y la ejecución de queries.
"""
import pyodbc
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import threading
from queue import Queue, Empty

from ..core import get_settings, get_logger

logger = get_logger(__name__)


class ODBCConnectionPool:
    """
    Pool de conexiones ODBC thread-safe.
    Reutiliza conexiones para mejor rendimiento.
    """

    def __init__(self, pool_size: int = 5):
        self.settings = get_settings()
        self.pool_size = pool_size
        self._pool: Queue = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False

    def _create_connection(self) -> pyodbc.Connection:
        """Crea una nueva conexión ODBC"""
        try:
            conn_string = f"DSN={self.settings.odbc_dsn}"

            if self.settings.odbc_user:
                conn_string += f";UID={self.settings.odbc_user}"
            if self.settings.odbc_password:
                conn_string += f";PWD={self.settings.odbc_password}"

            connection = pyodbc.connect(
                conn_string,
                timeout=self.settings.odbc_connection_timeout
            )
            connection.timeout = self.settings.odbc_query_timeout
            logger.info(f"Conexión ODBC creada: {self.settings.odbc_dsn}")
            return connection

        except pyodbc.Error as e:
            logger.error(f"Error al crear conexión ODBC: {e}")
            raise

    def initialize(self):
        """Inicializa el pool con conexiones"""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            logger.info(f"Inicializando pool de conexiones (tamaño: {self.pool_size})")
            for _ in range(self.pool_size):
                try:
                    conn = self._create_connection()
                    self._pool.put(conn)
                except Exception as e:
                    logger.error(f"Error al inicializar pool: {e}")
                    raise

            self._initialized = True
            logger.info("Pool de conexiones inicializado correctamente")

    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener una conexión del pool.

        Uso:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        if not self._initialized:
            self.initialize()

        connection = None
        try:
            # Obtener conexión del pool (esperar hasta 10 segundos)
            connection = self._pool.get(timeout=10)

            # Verificar que la conexión esté activa
            try:
                connection.cursor().execute("SELECT 1")
            except:
                logger.warning("Conexión inválida, creando nueva")
                connection = self._create_connection()

            yield connection

        except Empty:
            logger.error("Timeout esperando conexión del pool")
            raise Exception("No hay conexiones disponibles en el pool")

        finally:
            # Devolver conexión al pool
            if connection:
                try:
                    self._pool.put(connection, timeout=1)
                except:
                    logger.warning("No se pudo devolver conexión al pool")

    def close_all(self):
        """Cierra todas las conexiones del pool"""
        logger.info("Cerrando todas las conexiones del pool")
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except:
                pass
        self._initialized = False


class ODBCManager:
    """
    Gestor principal de operaciones ODBC.
    Proporciona métodos de alto nivel para queries.
    """

    def __init__(self, pool_size: int = 5):
        self.pool = ODBCConnectionPool(pool_size)
        self.settings = get_settings()

    def initialize(self):
        """Inicializa el gestor"""
        self.pool.initialize()

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query y retorna los resultados.

        Args:
            query: SQL query a ejecutar
            params: Parámetros para la query (opcional)
            fetch_all: Si es True, retorna todos los resultados

        Returns:
            Lista de diccionarios con los resultados
        """
        logger.info(f"Ejecutando query: {query[:100]}...")

        with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Obtener nombres de columnas
                columns = [column[0] for column in cursor.description]

                # Fetch results
                if fetch_all:
                    rows = cursor.fetchall()
                else:
                    rows = cursor.fetchmany(1000)  # Limitar a 1000 registros

                # Convertir a lista de diccionarios
                results = [
                    dict(zip(columns, row))
                    for row in rows
                ]

                logger.info(f"Query ejecutada exitosamente. Registros: {len(results)}")
                return results

            except pyodbc.Error as e:
                logger.error(f"Error ejecutando query: {e}")
                raise
            finally:
                cursor.close()

    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """
        Obtiene las columnas de una tabla.

        Args:
            table_name: Nombre de la tabla

        Returns:
            Lista de diccionarios con información de columnas
        """
        logger.info(f"Obteniendo columnas de tabla: {table_name}")

        with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                # Usar query simple para obtener metadata
                cursor.execute(f"SELECT TOP 1 * FROM {table_name}")

                columns = [
                    {
                        "name": column[0],
                        "type": str(column[1]),
                        "size": column[3] if column[3] else None,
                        "nullable": bool(column[6])
                    }
                    for column in cursor.description
                ]

                logger.info(f"Columnas obtenidas: {len(columns)}")
                return columns

            except pyodbc.Error as e:
                logger.error(f"Error obteniendo columnas: {e}")
                raise
            finally:
                cursor.close()

    def get_abends(
        self,
        region: Optional[str] = None,
        program: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtiene abends de CICS PA.

        Args:
            region: Región CICS (opcional)
            program: Nombre del programa (opcional)
            limit: Límite de registros

        Returns:
            Lista de abends
        """
        table = self.settings.abend_table_name
        query = f"SELECT TOP {limit} * FROM {table}"

        conditions = []
        params = []

        if region:
            conditions.append("CICS_REGION = ?")
            params.append(region)

        if program:
            conditions.append("PROGRAM_NAME LIKE ?")
            params.append(f"%{program}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY TIMESTAMP DESC"

        return self.execute_query(query, tuple(params) if params else None)

    def close(self):
        """Cierra el gestor y todas sus conexiones"""
        logger.info("Cerrando ODBCManager")
        self.pool.close_all()


# Instancia global (singleton)
_odbc_manager: Optional[ODBCManager] = None


def get_odbc_manager() -> ODBCManager:
    """
    Obtiene la instancia global del ODBCManager.
    Patrón singleton para reutilizar el pool.
    """
    global _odbc_manager

    if _odbc_manager is None:
        settings = get_settings()
        _odbc_manager = ODBCManager(pool_size=settings.pool_size)
        _odbc_manager.initialize()

    return _odbc_manager
