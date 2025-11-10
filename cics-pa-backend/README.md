# CICS PA Backend - Monitor de Abends

Backend REST API para monitoreo de **abends** (abnormal endings) en regiones CICS, conectándose a DVM mediante ODBC.

## Descripción

Sistema de monitoreo que consulta datos de **CICS Performance Analyzer (CICS PA)** para obtener información sobre fallos de programas en transacciones CICS. Proporciona endpoints REST para:

- Consultar abends por región CICS y programa
- Ejecutar queries personalizadas
- Obtener información de tablas
- Generar reportes y estadísticas

### Tecnologías

- **Python 3.8+**
- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **pyodbc** - Conexión ODBC a DVM
- **Uvicorn** - Servidor ASGI

## Estructura del Proyecto

```
cics-pa-backend/
├── src/
│   ├── api/                  # Endpoints REST
│   │   ├── health.py         # Health check
│   │   ├── tables.py         # Gestión de tablas
│   │   └── query.py          # Ejecución de queries
│   ├── core/                 # Configuración central
│   │   ├── config.py         # Settings
│   │   └── logging.py        # Sistema de logs
│   ├── database/             # Gestor ODBC
│   │   └── manager.py        # Pool de conexiones
│   ├── models/               # Modelos Pydantic
│   │   └── schemas.py        # Request/Response models
│   ├── services/             # Lógica de negocio
│   │   └── query_service.py  # Servicio de queries
│   └── main.py               # Aplicación FastAPI
├── tests/                    # Tests unitarios
├── docs/                     # Documentación
├── scripts/                  # Scripts de utilidad
└── requirements.txt          # Dependencias
```

## Instalación Rápida

### Linux/Mac

```bash
cd cics-pa-backend
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Windows

```cmd
cd cics-pa-backend
scripts\setup.bat
```

## Instalación Manual

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia `.env.example` a `.env` y configura:

```env
# DSN ODBC configurado
ODBC_DSN=DVM_DSN

# Credenciales (si aplica)
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password

# Nombre de la tabla de abends
ABEND_TABLE_NAME=CICS_ABENDS
```

### 4. Configurar ODBC

Ver [docs/ODBC_SETUP.md](docs/ODBC_SETUP.md) para instrucciones detalladas.

## Uso

### Iniciar el servidor

```bash
# Modo desarrollo
python -m src.main

# Modo producción
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

El servidor iniciará en `http://localhost:8000`

### Documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principales

### Health Check

```bash
GET /api/v1/health/
```

Verifica el estado del servicio y la conexión a base de datos.

### Obtener Abends

```bash
GET /api/v1/query/abends?region=PROD01&limit=100
```

Obtiene abends filtrados por región y programa.

**Parámetros:**
- `region` (opcional): Región CICS
- `program` (opcional): Nombre del programa
- `limit` (opcional): Límite de registros (default: 100)

### Ejecutar Query Personalizada

```bash
POST /api/v1/query/execute
Content-Type: application/json

{
  "query": "SELECT * FROM CICS_ABENDS WHERE CICS_REGION = ?",
  "params": ["PROD01"],
  "fetch_all": true
}
```

### Obtener Información de Tabla

```bash
GET /api/v1/tables/info/CICS_ABENDS
```

Retorna columnas y metadata de la tabla.

### Resumen Estadístico

```bash
GET /api/v1/query/abends/summary?region=PROD01
```

Genera estadísticas:
- Top 10 regiones con más abends
- Top 10 programas con más abends
- Top 10 códigos de abend más frecuentes

## Ejemplos de Uso

Ver [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md) para ejemplos detallados con curl, Python y JavaScript.

## Testing

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html
```

## Arquitectura

El backend sigue una arquitectura de capas:

1. **API Layer** (`api/`) - Endpoints FastAPI
2. **Service Layer** (`services/`) - Lógica de negocio
3. **Database Layer** (`database/`) - Gestión de conexiones ODBC
4. **Models Layer** (`models/`) - Validación con Pydantic
5. **Core Layer** (`core/`) - Configuración y logging

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para más detalles.

## Configuración Avanzada

### Pool de Conexiones

```env
POOL_SIZE=5           # Conexiones simultáneas
MAX_OVERFLOW=10       # Conexiones adicionales
POOL_RECYCLE=3600     # Reciclar conexiones (segundos)
```

### Timeouts

```env
ODBC_CONNECTION_TIMEOUT=30  # Timeout de conexión
ODBC_QUERY_TIMEOUT=300      # Timeout de query (5 min)
```

### Logging

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/backend.log   # Archivo de log
LOG_MAX_BYTES=10485760      # Tamaño máximo (10MB)
LOG_BACKUP_COUNT=5          # Archivos de rotación
```

## Buenas Prácticas Implementadas

- Validación automática con Pydantic
- Manejo centralizado de errores
- Pool de conexiones ODBC reutilizable
- Logging estructurado
- Documentación automática (OpenAPI)
- Tests unitarios
- Type hints en todo el código
- Separación de concerns (capas)

## Seguridad

- Validación de queries SQL (previene DROP, DELETE, etc.)
- Queries parametrizadas (previene SQL injection)
- Variables de entorno para credenciales
- Timeouts configurables

## Troubleshooting

### Error de conexión ODBC

```
pyodbc.Error: ('01000', "[01000] [unixODBC]...")
```

**Solución**: Verifica que el DSN esté configurado correctamente en `odbc.ini`

### Import error

```
ModuleNotFoundError: No module named 'src'
```

**Solución**: Ejecuta desde el directorio raíz: `python -m src.main`

Ver más en [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

MIT

## Contacto

Para dudas o sugerencias, abre un issue en el repositorio.

## Sobre CICS PA

**CICS Performance Analyzer** es una herramienta de IBM para análisis de performance en sistemas CICS Transaction Server, que procesa registros SMF (System Management Facility) para generar reportes de monitoreo y análisis de transacciones.
