# Ejemplos de Uso de la API

Esta guía muestra ejemplos prácticos de cómo usar cada endpoint de la API.

## Índice

1. [Health Check](#health-check)
2. [Obtener Abends](#obtener-abends)
3. [Resumen Estadístico](#resumen-estadístico)
4. [Ejecutar Query Personalizada](#ejecutar-query-personalizada)
5. [Información de Tabla](#información-de-tabla)
6. [Ejemplos con Cliente Python](#ejemplos-con-cliente-python)
7. [Ejemplos con JavaScript](#ejemplos-con-javascript)

---

## Health Check

Verifica que el servicio esté funcionando y pueda conectarse a la base de datos.

### curl

```bash
curl http://localhost:8000/api/v1/health/
```

### Respuesta

```json
{
  "status": "healthy",
  "timestamp": "2024-11-09T10:30:00.000000",
  "version": "1.0.0",
  "database_connected": true,
  "details": {
    "app_name": "CICS PA Abends Monitor",
    "odbc_dsn": "DVM_DSN",
    "pool_size": 5,
    "db_message": "Conexión exitosa"
  }
}
```

### Ping simple

```bash
curl http://localhost:8000/api/v1/health/ping
```

```json
{
  "message": "pong",
  "timestamp": "2024-11-09T10:30:00.000000"
}
```

---

## Obtener Abends

### 1. Todos los abends (últimos 100)

```bash
curl "http://localhost:8000/api/v1/query/abends?limit=100"
```

### 2. Filtrar por región CICS

```bash
curl "http://localhost:8000/api/v1/query/abends?region=PROD01&limit=50"
```

### 3. Filtrar por programa

```bash
curl "http://localhost:8000/api/v1/query/abends?program=PAYROLL&limit=20"
```

### 4. Filtrar por región y programa

```bash
curl "http://localhost:8000/api/v1/query/abends?region=PROD01&program=PAYROLL&limit=10"
```

### 5. Con POST (más flexible)

```bash
curl -X POST "http://localhost:8000/api/v1/query/abends" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "PROD01",
    "program": "PAYROLL",
    "limit": 50
  }'
```

### Respuesta típica

```json
{
  "success": true,
  "abends": [
    {
      "TIMESTAMP": "2024-11-09 10:30:00",
      "CICS_REGION": "PROD01",
      "PROGRAM_NAME": "PAYROLL",
      "ABEND_CODE": "ASRA",
      "TRANSACTION_ID": "PAY1",
      "USER_ID": "USER123",
      "TERMINAL_ID": "TERM01"
    },
    {
      "TIMESTAMP": "2024-11-09 10:25:00",
      "CICS_REGION": "PROD01",
      "PROGRAM_NAME": "PAYROLL",
      "ABEND_CODE": "AICA",
      "TRANSACTION_ID": "PAY1",
      "USER_ID": "USER456",
      "TERMINAL_ID": "TERM02"
    }
  ],
  "total": 2,
  "filters_applied": {
    "region": "PROD01",
    "program": "PAYROLL",
    "limit": 50
  }
}
```

---

## Resumen Estadístico

Obtiene estadísticas agregadas de abends.

### curl

```bash
curl "http://localhost:8000/api/v1/query/abends/summary?limit=1000"
```

### Con filtro de región

```bash
curl "http://localhost:8000/api/v1/query/abends/summary?region=PROD01&limit=500"
```

### Respuesta

```json
{
  "success": true,
  "summary": {
    "total_abends": 245,
    "top_regions": {
      "PROD01": 120,
      "PROD02": 80,
      "TEST01": 45
    },
    "top_programs": {
      "PAYROLL": 50,
      "INVOICE": 35,
      "CUSTOMER": 28
    },
    "top_abend_codes": {
      "ASRA": 100,
      "AICA": 75,
      "AKCP": 45
    },
    "unique_regions": 3,
    "unique_programs": 25,
    "unique_abend_codes": 8
  }
}
```

---

## Ejecutar Query Personalizada

Ejecuta queries SQL SELECT personalizadas.

### Ejemplo 1: Query simple

```bash
curl -X POST "http://localhost:8000/api/v1/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM CICS_ABENDS WHERE ABEND_CODE = '\''ASRA'\'' ORDER BY TIMESTAMP DESC",
    "fetch_all": true
  }'
```

### Ejemplo 2: Query con parámetros

```bash
curl -X POST "http://localhost:8000/api/v1/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM CICS_ABENDS WHERE CICS_REGION = ? AND ABEND_CODE = ? ORDER BY TIMESTAMP DESC",
    "params": ["PROD01", "ASRA"],
    "fetch_all": true
  }'
```

### Ejemplo 3: Contar abends por programa

```bash
curl -X POST "http://localhost:8000/api/v1/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT PROGRAM_NAME, COUNT(*) as COUNT FROM CICS_ABENDS GROUP BY PROGRAM_NAME ORDER BY COUNT DESC",
    "fetch_all": true
  }'
```

### Ejemplo 4: Abends de hoy

```bash
curl -X POST "http://localhost:8000/api/v1/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM CICS_ABENDS WHERE CAST(TIMESTAMP AS DATE) = CAST(GETDATE() AS DATE)",
    "fetch_all": true
  }'
```

### Respuesta

```json
{
  "success": true,
  "data": [
    {
      "PROGRAM_NAME": "PAYROLL",
      "COUNT": 50
    },
    {
      "PROGRAM_NAME": "INVOICE",
      "COUNT": 35
    }
  ],
  "row_count": 2,
  "execution_time_ms": 125.5
}
```

### Restricciones de seguridad

❌ **Queries NO permitidas** (DDL):

```sql
DROP TABLE CICS_ABENDS
DELETE FROM CICS_ABENDS
TRUNCATE TABLE CICS_ABENDS
ALTER TABLE CICS_ABENDS
CREATE TABLE nueva_tabla
```

✅ **Queries permitidas** (solo SELECT):

```sql
SELECT * FROM CICS_ABENDS
SELECT COUNT(*) FROM CICS_ABENDS
SELECT * FROM CICS_ABENDS WHERE ...
```

---

## Información de Tabla

Obtiene metadata de columnas de una tabla.

### Método 1: GET

```bash
curl "http://localhost:8000/api/v1/tables/info/CICS_ABENDS"
```

### Método 2: POST

```bash
curl -X POST "http://localhost:8000/api/v1/tables/info" \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "CICS_ABENDS"
  }'
```

### Respuesta

```json
{
  "table_name": "CICS_ABENDS",
  "columns": [
    {
      "name": "TIMESTAMP",
      "type": "<class 'datetime.datetime'>",
      "size": null,
      "nullable": false
    },
    {
      "name": "CICS_REGION",
      "type": "<class 'str'>",
      "size": 8,
      "nullable": false
    },
    {
      "name": "PROGRAM_NAME",
      "type": "<class 'str'>",
      "size": 8,
      "nullable": false
    },
    {
      "name": "ABEND_CODE",
      "type": "<class 'str'>",
      "size": 4,
      "nullable": true
    }
  ],
  "total_columns": 4
}
```

---

## Ejemplos con Cliente Python

### Script completo

```python
#!/usr/bin/env python3
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def health_check():
    """Verifica salud del servicio"""
    response = requests.get(f"{BASE_URL}/health/")
    return response.json()

def get_abends(region=None, program=None, limit=100):
    """Obtiene abends con filtros"""
    params = {"limit": limit}
    if region:
        params["region"] = region
    if program:
        params["program"] = program

    response = requests.get(f"{BASE_URL}/query/abends", params=params)
    return response.json()

def get_summary(region=None):
    """Obtiene resumen estadístico"""
    params = {}
    if region:
        params["region"] = region

    response = requests.get(f"{BASE_URL}/query/abends/summary", params=params)
    return response.json()

def execute_query(query, params=None):
    """Ejecuta query personalizada"""
    payload = {
        "query": query,
        "params": params or [],
        "fetch_all": True
    }
    response = requests.post(f"{BASE_URL}/query/execute", json=payload)
    return response.json()

# Ejemplos de uso
if __name__ == "__main__":
    # Health check
    print("=== Health Check ===")
    health = health_check()
    print(f"Status: {health['status']}")
    print(f"DB Connected: {health['database_connected']}")
    print()

    # Obtener abends de PROD01
    print("=== Abends de PROD01 ===")
    abends = get_abends(region="PROD01", limit=10)
    print(f"Total: {abends['total']}")
    for abend in abends['abends'][:3]:  # Primeros 3
        print(f"  - {abend['PROGRAM_NAME']}: {abend['ABEND_CODE']}")
    print()

    # Resumen estadístico
    print("=== Resumen ===")
    summary = get_summary()
    print(f"Total abends: {summary['summary']['total_abends']}")
    print("Top programas:")
    for prog, count in list(summary['summary']['top_programs'].items())[:3]:
        print(f"  - {prog}: {count}")
    print()

    # Query personalizada
    print("=== Query Personalizada ===")
    result = execute_query(
        "SELECT ABEND_CODE, COUNT(*) as COUNT FROM CICS_ABENDS GROUP BY ABEND_CODE",
    )
    print(f"Resultados: {result['row_count']}")
    for row in result['data'][:3]:
        print(f"  - {row['ABEND_CODE']}: {row['COUNT']}")
```

### Instalar requests

```bash
pip install requests
```

### Ejecutar

```bash
python ejemplos.py
```

---

## Ejemplos con JavaScript

### Con fetch (navegador o Node.js)

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Health check
async function healthCheck() {
  const response = await fetch(`${BASE_URL}/health/`);
  const data = await response.json();
  console.log("Status:", data.status);
  console.log("DB Connected:", data.database_connected);
}

// Obtener abends
async function getAbends(region = null, program = null, limit = 100) {
  const params = new URLSearchParams({ limit });
  if (region) params.append("region", region);
  if (program) params.append("program", program);

  const response = await fetch(`${BASE_URL}/query/abends?${params}`);
  const data = await response.json();
  return data;
}

// Ejecutar query
async function executeQuery(query, params = null) {
  const response = await fetch(`${BASE_URL}/query/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      params: params || [],
      fetch_all: true,
    }),
  });
  const data = await response.json();
  return data;
}

// Uso
(async () => {
  await healthCheck();

  const abends = await getAbends("PROD01", null, 10);
  console.log("Abends:", abends.total);

  const result = await executeQuery(
    "SELECT * FROM CICS_ABENDS WHERE ABEND_CODE = ?",
    ["ASRA"]
  );
  console.log("Query results:", result.row_count);
})();
```

### Con axios (Node.js)

```javascript
const axios = require("axios");

const BASE_URL = "http://localhost:8000/api/v1";

// Obtener abends
async function getAbends(region, limit = 100) {
  try {
    const response = await axios.get(`${BASE_URL}/query/abends`, {
      params: { region, limit },
    });
    return response.data;
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
    throw error;
  }
}

// Ejecutar query
async function executeQuery(query, params = []) {
  try {
    const response = await axios.post(`${BASE_URL}/query/execute`, {
      query,
      params,
      fetch_all: true,
    });
    return response.data;
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
    throw error;
  }
}

// Uso
(async () => {
  const abends = await getAbends("PROD01", 10);
  console.log(`Found ${abends.total} abends`);

  const result = await executeQuery(
    "SELECT COUNT(*) as total FROM CICS_ABENDS"
  );
  console.log("Total abends:", result.data[0].total);
})();
```

---

## Manejo de Errores

### Error 422: Validación fallida

```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "Query contiene keyword no permitida: DROP",
      "type": "value_error"
    }
  ]
}
```

### Error 500: Error del servidor

```json
{
  "success": false,
  "error": "Error ejecutando query: [ODBC Driver] Connection timeout",
  "error_type": "DatabaseConnectionError",
  "timestamp": "2024-11-09T10:30:00.000000"
}
```

---

## Testing con Postman

1. Importar colección desde URL: `http://localhost:8000/openapi.json`
2. O crear manualmente los requests con los ejemplos de arriba
3. Configurar variable de entorno: `base_url = http://localhost:8000`

---

## Documentación Interactiva

La mejor forma de probar la API es usando la documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Permite:
- Ver todos los endpoints
- Probar requests directamente
- Ver schemas de request/response
- Ver códigos de error
