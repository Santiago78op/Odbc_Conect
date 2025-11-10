"""
Configuración centralizada de la aplicación.
Usa variables de entorno con valores por defecto.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # API Settings
    app_name: str = "CICS PA Abends Monitor"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # ODBC Settings
    odbc_dsn: str = "DVM_DSN"
    odbc_user: Optional[str] = None
    odbc_password: Optional[str] = None
    odbc_connection_timeout: int = 30
    odbc_query_timeout: int = 300  # 5 minutos

    # Database Pool Settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600  # 1 hora

    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "logs/cics_pa_backend.log"
    log_max_bytes: int = 10485760  # 10MB
    log_backup_count: int = 5

    # CICS PA Specific
    default_cics_region: Optional[str] = None
    abend_table_name: str = "CICS_ABENDS"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la configuración de la aplicación (singleton).
    lru_cache asegura que solo se cree una instancia.
    """
    return Settings()
