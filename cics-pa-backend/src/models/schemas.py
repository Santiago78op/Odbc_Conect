"""
Modelos Pydantic para validación de requests y responses.
Define la estructura de datos de la API.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


# ========== Request Models ==========

class QueryRequest(BaseModel):
    """Request para ejecutar una query personalizada"""
    query: str = Field(..., description="SQL query a ejecutar", min_length=1)
    params: Optional[List[Any]] = Field(None, description="Parámetros de la query")
    fetch_all: bool = Field(True, description="Traer todos los resultados")

    @validator('query')
    def validate_query(cls, v):
        """Validación básica de seguridad SQL"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
        query_upper = v.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Query contiene keyword no permitida: {keyword}")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "query": "SELECT * FROM CICS_ABENDS WHERE CICS_REGION = ? ORDER BY TIMESTAMP DESC",
                "params": ["PROD01"],
                "fetch_all": True
            }
        }


class AbendsFilterRequest(BaseModel):
    """Request para filtrar abends"""
    region: Optional[str] = Field(None, description="Región CICS")
    program: Optional[str] = Field(None, description="Nombre del programa")
    limit: int = Field(100, description="Límite de registros", ge=1, le=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "region": "PROD01",
                "program": "PAYROLL",
                "limit": 50
            }
        }


class TableInfoRequest(BaseModel):
    """Request para obtener información de tabla"""
    table_name: str = Field(..., description="Nombre de la tabla", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "CICS_ABENDS"
            }
        }


# ========== Response Models ==========

class ColumnInfo(BaseModel):
    """Información de una columna"""
    name: str = Field(..., description="Nombre de la columna")
    type: str = Field(..., description="Tipo de dato")
    size: Optional[int] = Field(None, description="Tamaño de la columna")
    nullable: bool = Field(..., description="Permite valores NULL")


class TableInfoResponse(BaseModel):
    """Response con información de tabla"""
    table_name: str
    columns: List[ColumnInfo]
    total_columns: int

    class Config:
        json_schema_extra = {
            "example": {
                "table_name": "CICS_ABENDS",
                "columns": [
                    {
                        "name": "TIMESTAMP",
                        "type": "datetime",
                        "size": None,
                        "nullable": False
                    },
                    {
                        "name": "CICS_REGION",
                        "type": "str",
                        "size": 8,
                        "nullable": False
                    }
                ],
                "total_columns": 2
            }
        }


class QueryResponse(BaseModel):
    """Response genérico para queries"""
    success: bool = Field(..., description="Indicador de éxito")
    data: List[Dict[str, Any]] = Field(..., description="Datos retornados")
    row_count: int = Field(..., description="Número de registros")
    execution_time_ms: Optional[float] = Field(None, description="Tiempo de ejecución en ms")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {
                        "TIMESTAMP": "2024-11-09 10:30:00",
                        "CICS_REGION": "PROD01",
                        "PROGRAM_NAME": "PAYROLL",
                        "ABEND_CODE": "ASRA"
                    }
                ],
                "row_count": 1,
                "execution_time_ms": 125.5
            }
        }


class AbendRecord(BaseModel):
    """Modelo de un registro de abend"""
    timestamp: Optional[str] = Field(None, description="Fecha y hora del abend")
    cics_region: Optional[str] = Field(None, description="Región CICS")
    program_name: Optional[str] = Field(None, description="Nombre del programa")
    abend_code: Optional[str] = Field(None, description="Código de abend")
    transaction_id: Optional[str] = Field(None, description="ID de transacción")
    user_id: Optional[str] = Field(None, description="ID de usuario")
    terminal_id: Optional[str] = Field(None, description="ID de terminal")

    # Permite campos adicionales
    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "timestamp": "2024-11-09 10:30:00",
                "cics_region": "PROD01",
                "program_name": "PAYROLL",
                "abend_code": "ASRA",
                "transaction_id": "PAY1",
                "user_id": "USER123",
                "terminal_id": "TERM01"
            }
        }


class AbendsResponse(BaseModel):
    """Response para listado de abends"""
    success: bool
    abends: List[Dict[str, Any]]
    total: int
    filters_applied: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "abends": [
                    {
                        "timestamp": "2024-11-09 10:30:00",
                        "cics_region": "PROD01",
                        "program_name": "PAYROLL",
                        "abend_code": "ASRA"
                    }
                ],
                "total": 1,
                "filters_applied": {
                    "region": "PROD01",
                    "program": None,
                    "limit": 100
                }
            }
        }


class HealthResponse(BaseModel):
    """Response para health check"""
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(..., description="Timestamp del check")
    version: str = Field(..., description="Versión de la API")
    database_connected: bool = Field(..., description="Estado de conexión a base de datos")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-11-09T10:30:00",
                "version": "1.0.0",
                "database_connected": True,
                "details": {
                    "odbc_dsn": "DVM_DSN",
                    "pool_size": 5
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response estándar para errores"""
    success: bool = Field(False, description="Siempre False para errores")
    error: str = Field(..., description="Mensaje de error")
    error_type: str = Field(..., description="Tipo de error")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "No se pudo conectar a la base de datos",
                "error_type": "DatabaseConnectionError",
                "timestamp": "2024-11-09T10:30:00"
            }
        }
