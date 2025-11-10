# Arquitectura del Sistema

Este documento describe la arquitectura del backend de monitoreo de abends CICS PA.

## Visión General

El sistema sigue una **arquitectura en capas** (layered architecture) con separación clara de responsabilidades:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← Endpoints REST
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← Lógica de negocio
├─────────────────────────────────────┤
│      Database Layer (ODBC Pool)     │  ← Gestión de datos
├─────────────────────────────────────┤
│         Models (Pydantic)           │  ← Validación
├─────────────────────────────────────┤
│      Core (Config & Logging)        │  ← Configuración
└─────────────────────────────────────┘
```

## Capas del Sistema

### 1. Core Layer (`src/core/`)

**Responsabilidad**: Configuración centralizada y logging

**Componentes**:

- `config.py`: Gestión de configuración con Pydantic Settings
  - Carga variables de entorno desde `.env`
  - Proporciona valores por defecto
  - Singleton pattern con `@lru_cache`

- `logging.py`: Sistema de logging estructurado
  - Logs a archivo con rotación
  - Logs a consola
  - Formato consistente con timestamps

**Patrón de diseño**: Singleton

```python
from src.core import get_settings, get_logger

settings = get_settings()  # Siempre la misma instancia
logger = get_logger(__name__)
```

### 2. Models Layer (`src/models/`)

**Responsabilidad**: Validación de datos y schemas

**Componentes**:

- `schemas.py`: Modelos Pydantic para:
  - **Request models**: Validación de entrada (QueryRequest, AbendsFilterRequest)
  - **Response models**: Estructura de salida (QueryResponse, AbendsResponse)
  - **Validadores personalizados**: Prevención de SQL injection

**Beneficios**:
- Validación automática
- Documentación automática (OpenAPI)
- Type safety
- Conversión de tipos

```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    params: Optional[List[Any]] = None

    @validator('query')
    def validate_query(cls, v):
        # Validación personalizada
        if 'DROP' in v.upper():
            raise ValueError("Query no permitida")
        return v
```

### 3. Database Layer (`src/database/`)

**Responsabilidad**: Gestión de conexiones ODBC

**Componentes**:

- `manager.py`:
  - **ODBCConnectionPool**: Pool thread-safe de conexiones
  - **ODBCManager**: Gestor de alto nivel para operaciones

**Características**:

1. **Connection Pooling**:
   - Reutilización de conexiones
   - Thread-safe con locks
   - Verificación de conexiones activas

2. **Context Manager**:
   ```python
   with pool.get_connection() as conn:
       cursor = conn.cursor()
       cursor.execute(query)
   ```

3. **Métodos especializados**:
   - `execute_query()`: Ejecutar queries genéricas
   - `get_table_columns()`: Metadata de tablas
   - `get_abends()`: Query específica de abends

**Patrón de diseño**: Singleton + Object Pool

### 4. Service Layer (`src/services/`)

**Responsabilidad**: Lógica de negocio

**Componentes**:

- `query_service.py`: QueryService con métodos de negocio
  - `execute_custom_query()`: Ejecutar queries con timing
  - `get_abends()`: Obtener abends con filtros
  - `get_abends_summary()`: Estadísticas agregadas
  - `test_connection()`: Health check de DB

**Características**:

- Capa intermedia entre API y Database
- Manejo de errores consistente
- Logging de operaciones
- Transformación de datos

**Flujo de datos**:
```
API → Service → Database → DVM
      ↓         ↓
   Validación  Pool
   Logging     Connection
```

### 5. API Layer (`src/api/`)

**Responsabilidad**: Endpoints HTTP REST

**Componentes**:

- `health.py`: Health checks
  - `GET /health/`: Estado completo del sistema
  - `GET /health/ping`: Ping simple

- `tables.py`: Información de tablas
  - `GET /tables/info/{table_name}`: Metadata de tabla
  - `POST /tables/info`: Alternativa con body

- `query.py`: Operaciones de consulta
  - `POST /query/execute`: Query personalizada
  - `GET /query/abends`: Obtener abends
  - `POST /query/abends`: Alternativa con body
  - `GET /query/abends/summary`: Estadísticas

**Características**:

- Inyección de dependencias con FastAPI
- Manejo de errores con HTTPException
- Documentación automática (OpenAPI/Swagger)
- Validación automática con Pydantic

```python
@router.get("/abends", response_model=AbendsResponse)
async def get_abends(
    region: str = Query(None),
    service: QueryService = Depends(get_query_service)
):
    result = await service.get_abends(region=region)
    return result
```

## Patrones de Diseño Implementados

### 1. Singleton Pattern

**Usado en**: Settings, Logger, ODBCManager, QueryService

**Beneficio**: Una única instancia compartida

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2. Object Pool Pattern

**Usado en**: ODBCConnectionPool

**Beneficio**: Reutilización de conexiones costosas

```python
class ODBCConnectionPool:
    def __init__(self, pool_size: int):
        self._pool: Queue = Queue(maxsize=pool_size)

    @contextmanager
    def get_connection(self):
        connection = self._pool.get()
        yield connection
        self._pool.put(connection)
```

### 3. Dependency Injection

**Usado en**: FastAPI endpoints

**Beneficio**: Testabilidad y desacoplamiento

```python
def get_query_service() -> QueryService:
    return QueryService()

@router.get("/abends")
async def get_abends(service: QueryService = Depends(get_query_service)):
    return await service.get_abends()
```

### 4. Repository Pattern

**Usado en**: ODBCManager actúa como repository

**Beneficio**: Abstracción de acceso a datos

### 5. Middleware Pattern

**Usado en**: FastAPI middleware

**Beneficio**: Procesamiento transversal de requests

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log antes de procesar
    response = await call_next(request)
    # Log después de procesar
    return response
```

## Flujo de una Request

```
1. Cliente HTTP
   ↓
2. FastAPI (main.py)
   ↓ [Middleware de logging]
   ↓ [CORS]
3. Router (/api/v1/query/abends)
   ↓
4. Endpoint function (query.py)
   ↓ [Validación con Pydantic]
   ↓ [Inyección de dependencias]
5. Service Layer (query_service.py)
   ↓ [Lógica de negocio]
   ↓ [Logging]
6. Database Layer (manager.py)
   ↓ [Obtener conexión del pool]
   ↓ [Ejecutar query]
7. DVM via ODBC
   ↓ [Resultados]
8. ← Transformación (dict)
   ↓
9. ← Validación (Pydantic response model)
   ↓
10. ← JSON Response al cliente
```

## Manejo de Errores

### Estrategia por Capas

```
API Layer:
  - HTTPException con status codes apropiados
  - Respuestas JSON estructuradas

Service Layer:
  - Try/catch con logging
  - Re-raise exceptions para API layer

Database Layer:
  - pyodbc.Error específicos
  - Logging detallado de errores de conexión

Global:
  - Exception handler en main.py
  - Log de stack traces
```

### Ejemplo de flujo de error

```python
# Database Layer
try:
    cursor.execute(query)
except pyodbc.Error as e:
    logger.error(f"Error ODBC: {e}")
    raise

# Service Layer
try:
    result = self.odbc_manager.execute_query(query)
except Exception as e:
    logger.error(f"Error en servicio: {e}")
    raise

# API Layer
try:
    result = await service.execute_custom_query(query)
    return result
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## Configuración y Settings

### Variables de Entorno

```
.env → Settings (Pydantic) → Toda la aplicación
```

**Ventajas**:
- Type safety con Pydantic
- Validación automática
- Documentación integrada
- Valores por defecto

```python
class Settings(BaseSettings):
    odbc_dsn: str = "DVM_DSN"
    pool_size: int = 5

    class Config:
        env_file = ".env"
```

## Threading y Concurrencia

### FastAPI Async

- Endpoints declarados como `async def`
- No bloqueantes para I/O
- Maneja múltiples requests concurrentes

### Pool Thread-Safe

```python
class ODBCConnectionPool:
    def __init__(self):
        self._pool: Queue = Queue()  # Thread-safe
        self._lock = threading.Lock()  # Para inicialización
```

### Consideraciones

- pyodbc es thread-safe a nivel de conexión
- Cada request obtiene su propia conexión del pool
- Las conexiones se devuelven al pool después de usarse

## Seguridad

### 1. Prevención de SQL Injection

```python
# ❌ Vulnerable
cursor.execute(f"SELECT * FROM table WHERE id = {user_input}")

# ✅ Seguro (parametrizado)
cursor.execute("SELECT * FROM table WHERE id = ?", (user_input,))
```

### 2. Validación de Queries

```python
@validator('query')
def validate_query(cls, v):
    dangerous = ['DROP', 'DELETE', 'TRUNCATE']
    if any(kw in v.upper() for kw in dangerous):
        raise ValueError("Query no permitida")
    return v
```

### 3. Credenciales en .env

- No hardcoded en código
- .env en .gitignore
- Usar variables de entorno en producción

### 4. CORS Configurado

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠ Restringir en producción
    allow_credentials=True,
)
```

## Logging

### Niveles por Capa

- **DEBUG**: Detalles de operaciones internas
- **INFO**: Operaciones normales (requests, queries)
- **WARNING**: Situaciones anómalas pero manejables
- **ERROR**: Errores que requieren atención

### Formato

```
2024-11-09 10:30:00 | INFO     | src.api.query | get_abends:45 | Obteniendo abends: region=PROD01
```

## Performance

### Optimizaciones

1. **Connection Pooling**: Reutilización de conexiones
2. **Query Timeout**: Evita queries largas
3. **Lazy Loading**: Singleton con lru_cache
4. **Async FastAPI**: No bloqueante
5. **Limite de resultados**: fetch_all con límites

### Benchmarks típicos

- Health check: ~10ms
- Query simple: ~100-200ms
- Query compleja: ~500-1000ms

## Escalabilidad

### Horizontal (múltiples instancias)

```
Load Balancer
    ↓
┌───────────┬───────────┬───────────┐
│ Instance1 │ Instance2 │ Instance3 │
└───────────┴───────────┴───────────┘
         ↓
       DVM
```

Cada instancia tiene su propio pool de conexiones.

### Vertical (más recursos)

Ajustar pool de conexiones:

```env
POOL_SIZE=10        # Más conexiones
MAX_OVERFLOW=20     # Más overflow
```

## Testing

### Estructura de Tests

```
tests/
  ├── test_models.py     # Tests de Pydantic
  ├── test_api.py        # Tests de endpoints
  └── test_services.py   # Tests de servicios
```

### Mocking

```python
@pytest.fixture
def mock_query_service():
    service = MagicMock()
    service.get_abends = AsyncMock(return_value=...)
    return service

async def test_endpoint(mock_query_service):
    with patch("get_query_service", return_value=mock_query_service):
        # Test endpoint
```

## Monitoreo

### Métricas Importantes

1. **Disponibilidad**: Health check endpoint
2. **Latencia**: Tiempo de response de queries
3. **Errores**: Rate de errores 5xx
4. **Conexiones**: Pool utilization
5. **Queries**: Queries por segundo

### Logs a Monitorear

```bash
# Errores
grep ERROR logs/cics_pa_backend.log

# Queries lentas
grep "execution_time_ms" logs/cics_pa_backend.log | awk '$NF > 1000'

# Conexiones
grep "Pool" logs/cics_pa_backend.log
```

## Deployment

### Desarrollo

```bash
python -m src.main
```

### Producción

```bash
# Con Gunicorn + Uvicorn
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# O directamente con Uvicorn
uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

### Docker (ejemplo)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Mantenimiento

### Tareas Comunes

1. **Rotación de logs**: Automática con RotatingFileHandler
2. **Pool health**: Monitorear conexiones activas
3. **Updates**: Actualizar dependencias regularmente
4. **Backups**: No aplica (solo lectura)

### Upgrade de Dependencias

```bash
pip list --outdated
pip install -U fastapi uvicorn pydantic
pip freeze > requirements.txt
```

## Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pyodbc Wiki](https://github.com/mkleehammer/pyodbc/wiki)
