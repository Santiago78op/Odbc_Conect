# CICS PA Backend - Sistema de Monitoreo con Prometheus y Grafana

Sistema completo de monitoreo para CICS Performance Analyzer (CICS PA) utilizando FastAPI, Prometheus, Grafana y Alertmanager.

## 📋 Características

- ✅ **Backend FastAPI** con métricas de Prometheus integradas
- ✅ **Métricas HTTP** (latencia, throughput, errores)
- ✅ **Métricas ODBC** (conexiones, queries, performance)
- ✅ **Métricas de negocio** (abends de CICS por región/programa)
- ✅ **Métricas de sistema** (CPU, memoria)
- ✅ **Alertas automáticas** configurables
- ✅ **Dashboards Grafana** pre-configurados
- ✅ **Código PEP 8** compliant

## 🏗️ Arquitectura

```
┌─────────────────┐
│  CICS PA Backend│ ←── Requests HTTP
│   (FastAPI)     │
│   Puerto: 8000  │
└────────┬────────┘
         │ /metrics
         ↓
┌─────────────────┐
│   Prometheus    │ ←── Scraping cada 15s
│   Puerto: 9090  │     Almacena métricas (30 días)
└────────┬────────┘
         │
         ├──→ Evaluación de alertas
         │    ↓
         │   ┌─────────────────┐
         │   │  Alertmanager   │ ──→ Notificaciones
         │   │  Puerto: 9093   │     (Email/Slack)
         │   └─────────────────┘
         ↓
┌─────────────────┐
│     Grafana     │ ←── Visualización
│   Puerto: 3000  │
└─────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Desarrollo Rápido

```bash
# 1. Backend
cd cics-pa-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz
cd prometheus-2.48.0.linux-amd64
./prometheus --config.file=<path-to-repo>/monitoring/prometheus.yml

# 3. Grafana (instalación según tu SO)
sudo systemctl start grafana-server
```

Ver: [QUICKSTART.md](./QUICKSTART.md) para guía completa.

### Opción 2: Instalación en Producción

Ver: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) para instalación completa con systemd.

## 📊 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Backend API | http://localhost:8000/docs | - |
| Métricas | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Alertmanager | http://localhost:9093 | - |

## 📁 Estructura del Proyecto

```
Rioku/
├── cics-pa-backend/           # Backend FastAPI
│   ├── src/
│   │   ├── core/
│   │   │   ├── metrics.py     # Métricas de Prometheus
│   │   │   ├── middleware.py  # Middleware de captura
│   │   │   ├── config.py      # Configuración
│   │   │   └── logging.py     # Logging
│   │   ├── api/
│   │   │   ├── metrics.py     # Endpoint /metrics
│   │   │   ├── health.py      # Health checks
│   │   │   ├── tables.py      # API tablas
│   │   │   └── query.py       # API queries
│   │   ├── database/
│   │   │   └── manager.py     # Gestor ODBC (instrumentado)
│   │   └── main.py            # Aplicación principal
│   ├── requirements.txt       # Dependencias
│   └── .env.example           # Variables de entorno
├── monitoring/
│   ├── prometheus.yml         # Config Prometheus
│   ├── alert_rules.yml        # Reglas de alertas
│   ├── alertmanager.yml       # Config Alertmanager
│   └── grafana/
│       ├── datasources.yml    # Datasource Prometheus
│       ├── dashboards.yml     # Provider dashboards
│       └── dashboards/
│           └── cics-pa-backend-dashboard.json  # Dashboard principal
├── INSTALLATION_GUIDE.md      # Guía de instalación completa
├── QUICKSTART.md              # Inicio rápido
├── MONITORING_SETUP.md        # Documentación de monitoreo
└── README.md                  # Este archivo
```

## 📈 Métricas Disponibles

### HTTP
- `cics_pa_http_requests_total` - Requests por método/endpoint/status
- `cics_pa_http_request_duration_seconds` - Latencia de requests
- `cics_pa_http_requests_in_progress` - Requests activos

### Base de Datos
- `cics_pa_db_connections_active` - Conexiones ODBC activas
- `cics_pa_db_query_duration_seconds` - Duración de queries
- `cics_pa_db_connection_errors_total` - Errores de conexión

### Negocio
- `cics_pa_abends_total` - Abends de CICS por región/programa
- `cics_pa_regions_monitored` - Regiones CICS monitoreadas

### Sistema
- `cics_pa_application_memory_usage_bytes` - Uso de memoria
- `cics_pa_application_cpu_usage_percent` - Uso de CPU

Ver todas las métricas: http://localhost:8000/metrics

## 🔔 Alertas Configuradas

- **ApplicationDown**: Backend no responde
- **HighErrorRate**: >5% errores HTTP 5xx
- **HighRequestLatency**: Latencia p95 >5s
- **DatabaseConnectionErrors**: Errores de conexión ODBC
- **HighMemoryUsage**: Memoria >2GB
- **HighAbendRate**: Alta tasa de abends en CICS

Ver: [MONITORING_SETUP.md](./MONITORING_SETUP.md#alertas-configuradas)

## 📊 Dashboard de Grafana

El dashboard incluye:
- Estado general de la aplicación
- Tasa y latencia de requests HTTP
- Métricas de base de datos ODBC
- Abends de CICS por región
- Uso de recursos (CPU/memoria)

![Dashboard Preview](docs/dashboard-preview.png)

## 🛠️ Desarrollo

### Requisitos

- Python 3.11+
- ODBC drivers configurados
- Acceso a DVM (Data Virtualization Manager)

### Setup de Desarrollo

```bash
# Clonar repositorio
git clone <repo-url>
cd Rioku/cics-pa-backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para testing

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar tests
pytest

# Iniciar en modo desarrollo
python -m uvicorn src.main:app --reload
```

### Agregar Nuevas Métricas

```python
# En src/core/metrics.py
from prometheus_client import Counter

my_metric = Counter(
    'cics_pa_my_metric',
    'Descripción de la métrica',
    ['label1', 'label2']
)

# En tu código
from src.core.metrics import my_metric

my_metric.labels(label1='value', label2='value').inc()
```

### Estilo de Código

El proyecto sigue **PEP 8** estrictamente:

```bash
# Verificar estilo
flake8 src/

# Formatear código
black src/
```

## 📚 Documentación

- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Instalación paso a paso
- [QUICKSTART.md](./QUICKSTART.md) - Inicio rápido para desarrollo
- [MONITORING_SETUP.md](./MONITORING_SETUP.md) - Guía completa de monitoreo
- [monitoring/README.md](./monitoring/README.md) - Configuración de monitoreo

## 🔒 Seguridad

### Recomendaciones

1. Cambiar credenciales por defecto de Grafana
2. Configurar HTTPS con certificados válidos
3. Usar secrets manager para credenciales ODBC
4. Configurar autenticación en Prometheus/Alertmanager
5. Restringir acceso con firewall

### Configurar HTTPS

```bash
# Generar certificado self-signed (desarrollo)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365

# Iniciar con HTTPS
uvicorn src.main:app --host 0.0.0.0 --port 8443 \
  --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Ver logs
sudo journalctl -u cics-pa-backend -n 50

# Verificar ODBC
odbcinst -j
isql -v DVM_DSN
```

### Prometheus no scraped backend

```bash
# Verificar configuración
promtool check config prometheus.yml

# Verificar métricas endpoint
curl http://localhost:8000/metrics
```

### Grafana no muestra datos

1. Configuration → Data Sources → Prometheus → Test
2. Verificar URL: http://localhost:9090
3. Verificar que Prometheus tenga datos

Ver: [MONITORING_SETUP.md#troubleshooting](./MONITORING_SETUP.md#troubleshooting)

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

### Lineamientos

- Seguir PEP 8
- Agregar tests para nuevas funcionalidades
- Documentar nuevas métricas
- Actualizar CHANGELOG.md

## 📝 Licencia

[Especificar licencia]

## 👥 Autores

- Equipo CICS PA

## 🙏 Agradecimientos

- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**Versión**: 1.0.0
**Última actualización**: 2025-11-16

Para soporte, abrir un issue o contactar al equipo de CICS PA.
