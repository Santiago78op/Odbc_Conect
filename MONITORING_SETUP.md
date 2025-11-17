# Guía de Configuración y Uso del Sistema de Monitoreo
# CICS PA Backend - Prometheus, Grafana y Alertmanager

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Requisitos Previos](#requisitos-previos)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Uso del Sistema](#uso-del-sistema)
6. [Métricas Disponibles](#métricas-disponibles)
7. [Alertas Configuradas](#alertas-configuradas)
8. [Dashboards de Grafana](#dashboards-de-grafana)
9. [Mantenimiento](#mantenimiento)
10. [Troubleshooting](#troubleshooting)

---

## Introducción

Este documento describe el sistema completo de monitoreo y observabilidad implementado para el backend de CICS PA. El sistema utiliza:

- **Prometheus**: Recolección y almacenamiento de métricas
- **Grafana**: Visualización de métricas en dashboards
- **Alertmanager**: Gestión y notificación de alertas

### Características Principales

- ✅ Métricas HTTP (latencia, throughput, errores)
- ✅ Métricas de base de datos ODBC (conexiones, queries, errores)
- ✅ Métricas de negocio (abends de CICS)
- ✅ Métricas de recursos del sistema (CPU, memoria)
- ✅ Alertas automáticas configurables
- ✅ Dashboards pre-configurados
- ✅ Cumplimiento con PEP 8

---

## Arquitectura

```
┌─────────────────┐
│  CICS PA Backend│ ←──── Requests de usuarios
│   (FastAPI)     │
│   Puerto: 8000  │
└────────┬────────┘
         │ /metrics
         │ (expone métricas)
         ↓
┌─────────────────┐
│   Prometheus    │ ←──── Scraping cada 15s
│   Puerto: 9090  │
└────────┬────────┘
         │
         ├──→ Almacenamiento (30 días)
         │
         ├──→ Evaluación de reglas de alertas
         │    │
         │    ↓
         │   ┌─────────────────┐
         │   │  Alertmanager   │ ──→ Email/Slack/Webhook
         │   │  Puerto: 9093   │
         │   └─────────────────┘
         │
         ↓
┌─────────────────┐
│     Grafana     │ ←──── Visualización
│   Puerto: 3000  │        (admin/admin)
└─────────────────┘
```

---

## Requisitos Previos

### Software Necesario

- Python 3.11+
- ODBC drivers configurados
- Prometheus 2.48.0+
- Grafana 10.0+
- Alertmanager 0.26.0+ (opcional)

### Recursos Mínimos Recomendados

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 25 GB (para métricas de 30 días)

---

## Instalación y Configuración

Para una guía detallada de instalación paso a paso, consultar:
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Instalación completa con systemd
- [QUICKSTART.md](./QUICKSTART.md) - Inicio rápido para desarrollo

### Resumen de Instalación

1. **Backend**: Instalar Python 3.11+, crear virtualenv, instalar requirements.txt
2. **Prometheus**: Descargar binario, configurar prometheus.yml
3. **Alertmanager**: Descargar binario, configurar alertmanager.yml
4. **Grafana**: Instalar via package manager, configurar datasource
5. **Systemd**: Configurar servicios para auto-inicio (producción)

---

## Uso del Sistema

### Acceso a las Interfaces Web

| Servicio       | URL                      | Credenciales    |
|----------------|--------------------------|-----------------|
| Backend API    | http://localhost:8000    | N/A             |
| Swagger Docs   | http://localhost:8000/docs | N/A          |
| Prometheus     | http://localhost:9090    | N/A             |
| Grafana        | http://localhost:3000    | admin/admin     |
| Alertmanager   | http://localhost:9093    | N/A             |

### Iniciar Servicios

#### Desarrollo (manual)

```bash
# Terminal 1: Backend
cd cics-pa-backend
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Prometheus
/opt/prometheus/prometheus --config.file=/opt/prometheus/prometheus.yml

# Terminal 3: Alertmanager (opcional)
/opt/alertmanager/alertmanager --config.file=/opt/alertmanager/alertmanager.yml
```

#### Producción (systemd)

```bash
sudo systemctl start cics-pa-backend
sudo systemctl start prometheus
sudo systemctl start alertmanager
sudo systemctl start grafana-server
```

### Primera Configuración de Grafana

1. Acceder a http://localhost:3000
2. Login: `admin` / `admin`
3. Cambiar password (recomendado)
4. El datasource de Prometheus ya está configurado (si seguiste la guía de instalación)
5. Ir a Dashboards → Browse → Carpeta "CICS PA"
6. Abrir "CICS PA Backend - Monitoreo Completo"

---

## Métricas Disponibles

### Métricas HTTP

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `cics_pa_http_requests_total` | Counter | Total de requests HTTP por método/endpoint/status |
| `cics_pa_http_request_duration_seconds` | Histogram | Duración de requests en segundos |
| `cics_pa_http_request_size_bytes` | Histogram | Tamaño de requests en bytes |
| `cics_pa_http_response_size_bytes` | Histogram | Tamaño de responses en bytes |
| `cics_pa_http_requests_in_progress` | Gauge | Requests actualmente en progreso |

### Métricas de Base de Datos

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `cics_pa_db_connections_active` | Gauge | Conexiones ODBC activas en el pool |
| `cics_pa_db_connections_total` | Counter | Total de conexiones creadas (success/error) |
| `cics_pa_db_query_duration_seconds` | Histogram | Duración de queries ODBC |
| `cics_pa_db_queries_total` | Counter | Total de queries por operación/tabla/status |
| `cics_pa_db_connection_errors_total` | Counter | Errores de conexión por tipo |
| `cics_pa_db_query_errors_total` | Counter | Errores en queries por tipo |

### Métricas de Negocio

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `cics_pa_abends_total` | Counter | Total de abends por región/programa/código |
| `cics_pa_abends_query_total` | Counter | Total de consultas de abends |
| `cics_pa_regions_monitored` | Gauge | Número de regiones CICS monitoreadas |

### Métricas de Sistema

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `cics_pa_application_memory_usage_bytes` | Gauge | Uso de memoria de la aplicación |
| `cics_pa_application_cpu_usage_percent` | Gauge | Uso de CPU de la aplicación |
| `cics_pa_application_exceptions_total` | Counter | Total de excepciones por tipo/endpoint |

### Consultas PromQL de Ejemplo

```promql
# Tasa de requests por segundo
rate(cics_pa_http_requests_total[5m])

# Latencia percentil 95
histogram_quantile(0.95, sum(rate(cics_pa_http_request_duration_seconds_bucket[5m])) by (le, endpoint))

# Tasa de errores HTTP 5xx
sum(rate(cics_pa_http_requests_total{status_code=~"5.."}[5m])) / sum(rate(cics_pa_http_requests_total[5m]))

# Top 10 programas con más abends
topk(10, sum(increase(cics_pa_abends_total[1h])) by (program))
```

---

## Alertas Configuradas

### Alertas Críticas

| Alerta | Condición | Severidad | Acción |
|--------|-----------|-----------|--------|
| ApplicationDown | Aplicación no responde por 1 min | Critical | Verificar logs y contenedor |
| CriticalErrorRate | >20% de errores 5xx por 2 min | Critical | Revisar logs y DVM |
| DatabaseConnectionErrors | Errores de conexión ODBC | Critical | Verificar ODBC/DSN |
| CriticalMemoryUsage | Memoria >4GB por 2 min | Critical | Reiniciar o escalar |

### Alertas de Warning

| Alerta | Condición | Severidad | Acción |
|--------|-----------|-----------|--------|
| HighErrorRate | >5% de errores 5xx por 5 min | Warning | Investigar logs |
| HighRequestLatency | p95 >5s por 5 min | Warning | Optimizar queries |
| SlowDatabaseQueries | Queries >30s (p95) por 5 min | Warning | Revisar índices |
| HighCPUUsage | CPU >80% por 10 min | Warning | Revisar procesos |

### Configuración de Notificaciones

Las alertas se envían a diferentes equipos según el componente:

- **Critical**: Oncall + Manager (email + webhook)
- **Database**: DBA Team
- **Business**: CICS Business Team
- **Performance**: Performance Team
- **Monitoring**: Monitoring Team

---

## Dashboards de Grafana

### Dashboard Principal: "CICS PA Backend - Monitoreo Completo"

El dashboard incluye las siguientes secciones:

#### 1. Estado General
- Estado de la aplicación (UP/DOWN)
- Tasa de requests HTTP
- Distribución por código de estado
- Latencia p95

#### 2. Rendimiento HTTP
- Latencia por endpoint (p50, p95, p99)
- Requests en progreso
- Throughput por método

#### 3. Base de Datos ODBC
- Conexiones activas
- Duración de queries (p95)
- Tasa de queries por operación
- Errores de conexión

#### 4. Métricas de Negocio
- Tasa de abends por región CICS
- Top 10 códigos de abend
- Consultas de abends

#### 5. Recursos del Sistema
- Uso de memoria (gauge)
- Uso de CPU (gauge)

### Personalización de Dashboards

1. Hacer clic en el título del panel → Edit
2. Modificar query PromQL
3. Ajustar opciones de visualización
4. Save Dashboard

---

## Mantenimiento

### Retención de Datos

**Prometheus**:
- Retención: 30 días
- Tamaño máximo: 10GB
- Ubicación: volumen `prometheus-data`

Para modificar:
```yaml
# En docker-compose.monitoring.yml
command:
  - '--storage.tsdb.retention.time=60d'  # Cambiar a 60 días
  - '--storage.tsdb.retention.size=20GB'  # Cambiar a 20GB
```

### Backups

**Grafana Dashboards**:
```bash
# Exportar dashboard
curl -H "Authorization: Bearer API_TOKEN" \
  http://localhost:3000/api/dashboards/uid/cics-pa-backend > backup.json
```

**Prometheus Data**:
```bash
# Backup de datos
tar czf prometheus-backup-$(date +%Y%m%d).tar.gz /opt/prometheus/data
```

**Configuración**:
```bash
# Backup de archivos de configuración
tar czf config-backup-$(date +%Y%m%d).tar.gz \
  cics-pa-backend/.env \
  /opt/prometheus/prometheus.yml \
  /opt/alertmanager/alertmanager.yml \
  /etc/grafana/provisioning
```

### Limpieza

```bash
# Detener servicios
sudo systemctl stop cics-pa-backend
sudo systemctl stop prometheus
sudo systemctl stop alertmanager
sudo systemctl stop grafana-server

# Limpiar datos (¡CUIDADO! Elimina métricas)
rm -rf /opt/prometheus/data/*
rm -rf /opt/alertmanager/data/*

# Limpiar logs
rm -rf cics-pa-backend/logs/*
```

---

## Troubleshooting

### Problema: No se ven métricas en Grafana

**Solución**:
1. Verificar que Prometheus está scraping el backend:
   ```bash
   # Ir a http://localhost:9090/targets
   # Verificar que "cics-pa-backend" está UP
   ```

2. Verificar el endpoint /metrics:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. Verificar datasource en Grafana:
   ```
   Settings → Data Sources → Prometheus → Test
   ```

### Problema: Alertas no se envían

**Solución**:
1. Verificar configuración de Alertmanager:
   ```bash
   docker-compose -f docker-compose.monitoring.yml logs alertmanager
   ```

2. Verificar que las alertas están en estado "Firing":
   ```
   http://localhost:9090/alerts
   ```

3. Verificar configuración SMTP en `alertmanager.yml`

### Problema: Alto uso de disco

**Solución**:
1. Reducir retención de Prometheus
2. Limpiar datos antiguos:
   ```bash
   # Conectarse al contenedor
   docker exec -it prometheus sh
   # Eliminar datos antiguos manualmente (con cuidado)
   ```

### Problema: Backend no inicia

**Solución**:
1. Verificar logs:
   ```bash
   # Si usa systemd
   sudo journalctl -u cics-pa-backend -n 100 --no-pager

   # Si inicio manual
   # Ver error en la terminal
   ```

2. Verificar configuración ODBC:
   ```bash
   odbcinst -j
   isql -v DVM_DSN
   ```

3. Verificar variables de entorno en `.env`
   ```bash
   cat cics-pa-backend/.env
   ```

---

## Mejores Prácticas

### Desarrollo

1. **Agregar nuevas métricas**:
   ```python
   # En src/core/metrics.py
   from prometheus_client import Counter

   my_custom_metric = Counter(
       'cics_pa_custom_metric',
       'Descripción de la métrica',
       ['label1', 'label2']
   )

   # En tu código
   my_custom_metric.labels(label1='value1', label2='value2').inc()
   ```

2. **Seguir PEP 8**:
   ```bash
   # Verificar estilo
   flake8 src/
   black src/
   ```

3. **Documentar métricas**: Incluir descripción clara en docstrings

### Producción

1. **Cambiar credenciales por defecto** de Grafana
2. **Configurar HTTPS** para todas las interfaces web
3. **Restringir acceso** con firewall o autenticación
4. **Configurar backups automáticos**
5. **Monitorear el sistema de monitoreo** (meta-monitoring)

---

## Recursos Adicionales

- [Documentación de Prometheus](https://prometheus.io/docs/)
- [Documentación de Grafana](https://grafana.com/docs/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)

---

## Soporte

Para reportar problemas o solicitar funcionalidades:
- Crear un issue en el repositorio
- Contactar al equipo de CICS PA

**Versión**: 1.0.0
**Última actualización**: 2025-11-16
