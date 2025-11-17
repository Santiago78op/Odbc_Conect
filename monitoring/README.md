# Configuración de Monitoreo - CICS PA Backend

Este directorio contiene la configuración completa del stack de monitoreo para el backend de CICS PA.

## Estructura de Archivos

```
monitoring/
├── prometheus.yml           # Configuración de Prometheus
├── alert_rules.yml          # Reglas de alertas
├── alertmanager.yml         # Configuración de Alertmanager
├── grafana/
│   ├── datasources.yml      # Configuración de datasources
│   ├── dashboards.yml       # Configuración de dashboards
│   └── dashboards/
│       └── cics-pa-backend-dashboard.json  # Dashboard principal
└── README.md                # Este archivo
```

## Componentes

### 1. Prometheus (`prometheus.yml`)

Servidor de métricas que recopila datos del backend cada 15 segundos.

**Configuración clave**:
- Scrape interval: 15s
- Retención: 30 días
- Targets: Backend (port 8000), Prometheus, Alertmanager, Node Exporter

### 2. Reglas de Alertas (`alert_rules.yml`)

Define condiciones para disparar alertas automáticas.

**Grupos de alertas**:
- `application_health`: Disponibilidad y errores
- `application_performance`: Latencia y rendimiento
- `database_health`: Estado de ODBC/DVM
- `system_resources`: CPU y memoria
- `business_metrics`: Abends de CICS
- `monitoring_health`: Estado del monitoreo

### 3. Alertmanager (`alertmanager.yml`)

Gestiona el enrutamiento y envío de alertas.

**⚠️ IMPORTANTE**: Configurar antes de usar en producción:
- SMTP settings (líneas 12-17)
- Slack webhook (si se usa)
- Emails de destinatarios

### 4. Grafana

Visualización de métricas en dashboards interactivos.

**Datasource**: Prometheus (pre-configurado)
**Dashboard**: CICS PA Backend - Monitoreo Completo

## Inicio Rápido

```bash
# Desde el directorio raíz del proyecto
docker-compose -f docker-compose.monitoring.yml up -d

# Acceder a:
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Alertmanager: http://localhost:9093
```

## Personalización

### Modificar Intervalos de Scraping

Editar `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s  # Cambiar aquí
```

### Agregar Nuevas Alertas

Editar `alert_rules.yml`:
```yaml
- alert: MiNuevaAlerta
  expr: mi_metrica > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Descripción breve"
    description: "Descripción detallada"
```

### Configurar Notificaciones

Editar `alertmanager.yml` y actualizar:
- `smtp_*`: Configuración de email
- `receivers`: Destinatarios y canales

## Seguridad

🔒 **Archivo sensible**: `alertmanager.yml` contiene credenciales

**Recomendaciones**:
1. No commitear passwords en git
2. Usar variables de entorno para secretos
3. Configurar autenticación en Grafana
4. Habilitar HTTPS en producción

## Documentación Completa

Ver: [MONITORING_SETUP.md](../MONITORING_SETUP.md)
