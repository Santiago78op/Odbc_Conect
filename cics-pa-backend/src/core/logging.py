"""
Sistema de logging centralizado para la aplicación.
Configura logs tanto a archivo como a consola.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import get_settings


class LoggerSetup:
    """Configurador centralizado de logging"""

    def __init__(self):
        self.settings = get_settings()
        self._logger: Optional[logging.Logger] = None

    def setup(self) -> logging.Logger:
        """
        Configura el sistema de logging con handlers de archivo y consola.
        """
        if self._logger:
            return self._logger

        # Crear logger principal
        logger = logging.getLogger("cics_pa_backend")
        logger.setLevel(getattr(logging, self.settings.log_level.upper()))
        logger.propagate = False

        # Evitar duplicados
        if logger.handlers:
            logger.handlers.clear()

        # Formato de logs
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler para archivo (con rotación)
        try:
            log_file = Path(self.settings.log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=self.settings.log_max_bytes,
                backupCount=self.settings.log_backup_count,
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"No se pudo crear el handler de archivo: {e}")

        self._logger = logger
        return logger


def get_logger(name: str = "cics_pa_backend") -> logging.Logger:
    """
    Obtiene un logger configurado.

    Args:
        name: Nombre del logger (por defecto usa el logger principal)

    Returns:
        Logger configurado
    """
    if name == "cics_pa_backend":
        setup = LoggerSetup()
        return setup.setup()
    else:
        return logging.getLogger(name)
