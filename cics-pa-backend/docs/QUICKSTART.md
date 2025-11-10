# Guía de Inicio Rápido

Esta guía te llevará desde cero a tener el backend funcionando en **menos de 5 minutos**.

## Prerrequisitos

- Python 3.8 o superior
- Acceso a DVM con ODBC configurado
- Git (opcional)

## Paso 1: Obtener el código

```bash
# Si tienes Git
git clone <repositorio>
cd cics-pa-backend

# O simplemente descomprime el ZIP
cd cics-pa-backend
```

## Paso 2: Setup automático

### Linux/Mac

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Windows

```cmd
scripts\setup.bat
```

Esto hará:
- Crear entorno virtual Python
- Instalar todas las dependencias
- Crear archivo `.env` desde plantilla

## Paso 3: Configurar ODBC

Edita el archivo `.env` creado:

```env
ODBC_DSN=tu_dsn_aqui
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password
ABEND_TABLE_NAME=CICS_ABENDS
```

**Nota**: El DSN debe estar configurado en tu sistema. Ver [ODBC_SETUP.md](ODBC_SETUP.md) si necesitas ayuda.

## Paso 4: Iniciar el servidor

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Iniciar servidor
python -m src.main
```

Verás algo como:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Paso 5: Probar la API

Abre tu navegador en:

```
http://localhost:8000/docs
```

Verás la documentación interactiva **Swagger UI** donde puedes probar todos los endpoints.

### Prueba rápida con curl

```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Obtener abends
curl "http://localhost:8000/api/v1/query/abends?limit=10"
```

## Próximos Pasos

1. **Lee la documentación de la API**: [API_EXAMPLES.md](API_EXAMPLES.md)
2. **Entiende la arquitectura**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Personaliza la configuración**: Edita `.env` según tus necesidades

## Troubleshooting Rápido

### "No se puede conectar a la base de datos"

- Verifica que el DSN existe: `odbcinst -q -s` (Linux)
- Prueba la conexión: `isql tu_dsn usuario password`
- Revisa las credenciales en `.env`

### "ModuleNotFoundError"

- Asegúrate de estar en el directorio raíz del proyecto
- Verifica que el entorno virtual esté activado
- Ejecuta con: `python -m src.main`

### "Puerto 8000 ya en uso"

Cambia el puerto en `.env`:

```env
PORT=8080
```

## Comandos Útiles

```bash
# Activar entorno virtual
source venv/bin/activate

# Desactivar entorno virtual
deactivate

# Ver logs en tiempo real
tail -f logs/cics_pa_backend.log

# Ejecutar tests
pytest

# Ver documentación API
open http://localhost:8000/docs
```

## Configuración Mínima

Solo necesitas estos valores en `.env`:

```env
ODBC_DSN=tu_dsn
ABEND_TABLE_NAME=CICS_ABENDS
```

El resto usa valores por defecto razonables.

## Verificar Instalación

```bash
# Verificar Python
python --version

# Verificar dependencias
pip list | grep -E "fastapi|uvicorn|pyodbc"

# Verificar ODBC
python -c "import pyodbc; print(pyodbc.drivers())"
```

## Ayuda Adicional

- **Documentación completa**: [README.md](../README.md)
- **Configuración ODBC**: [ODBC_SETUP.md](ODBC_SETUP.md)
- **Ejemplos de uso**: [API_EXAMPLES.md](API_EXAMPLES.md)

¡Listo! Ya tienes el backend funcionando. 🚀
