# Guía de Instalación - CICS PA Backend con Prometheus y Grafana

Guía completa para instalar el stack de monitoreo de forma nativa (sin Docker).

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación del Backend CICS PA](#instalación-del-backend-cics-pa)
3. [Instalación de Prometheus](#instalación-de-prometheus)
4. [Instalación de Alertmanager](#instalación-de-alertmanager)
5. [Instalación de Grafana](#instalación-de-grafana)
6. [Configuración del Sistema](#configuración-del-sistema)
7. [Inicio de Servicios](#inicio-de-servicios)
8. [Verificación](#verificación)
9. [Servicios como Systemd](#servicios-como-systemd)

---

## Requisitos Previos

### Sistema Operativo

- Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- Windows con WSL2
- macOS 11+

### Software Base

```bash
# Python 3.11 o superior
python3 --version

# pip (gestor de paquetes de Python)
pip3 --version

# ODBC (para conexión a DVM)
odbcinst -j
```

### Recursos Mínimos

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 25 GB libres

---

## Instalación del Backend CICS PA

### 1. Clonar el Repositorio

```bash
cd /opt
git clone <tu-repositorio> cics-pa
cd cics-pa/cics-pa-backend
```

### 2. Crear Entorno Virtual de Python

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env`:

```bash
cat > .env << 'EOF'
# Configuración de aplicación
APP_NAME=CICS PA Abends Monitor
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Servidor
HOST=0.0.0.0
PORT=8000

# ODBC - AJUSTAR SEGÚN TU ENTORNO
ODBC_DSN=DVM_DSN
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password
ODBC_CONNECTION_TIMEOUT=30
ODBC_QUERY_TIMEOUT=300

# Pool de conexiones
POOL_SIZE=5
MAX_OVERFLOW=10
POOL_RECYCLE=3600
EOF
```

### 5. Crear Directorio de Logs

```bash
mkdir -p logs
```

### 6. Verificar Instalación

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Acceder a: http://localhost:8000/docs

---

## Instalación de Prometheus

### 1. Descargar Prometheus

```bash
cd /opt
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz
mv prometheus-2.48.0.linux-amd64 prometheus
cd prometheus
```

### 2. Configurar Prometheus

```bash
# Copiar configuración desde el repositorio
cp /opt/cics-pa/monitoring/prometheus.yml /opt/prometheus/prometheus.yml
cp /opt/cics-pa/monitoring/alert_rules.yml /opt/prometheus/alert_rules.yml
```

Editar `/opt/prometheus/prometheus.yml` y ajustar targets:

```yaml
scrape_configs:
  - job_name: 'cics-pa-backend'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'localhost:8000'  # Ajustar según tu configuración
        labels:
          service: 'backend'
```

### 3. Crear Usuario para Prometheus

```bash
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus
```

### 4. Verificar Configuración

```bash
/opt/prometheus/prometheus --config.file=/opt/prometheus/prometheus.yml --web.enable-lifecycle --storage.tsdb.path=/opt/prometheus/data
```

Acceder a: http://localhost:9090

---

## Instalación de Alertmanager

### 1. Descargar Alertmanager

```bash
cd /opt
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
tar xvfz alertmanager-0.26.0.linux-amd64.tar.gz
mv alertmanager-0.26.0.linux-amd64 alertmanager
cd alertmanager
```

### 2. Configurar Alertmanager

```bash
# Copiar configuración
cp /opt/cics-pa/monitoring/alertmanager.yml /opt/alertmanager/alertmanager.yml
```

Editar `/opt/alertmanager/alertmanager.yml` y configurar SMTP:

```yaml
global:
  smtp_from: 'alerts@tu-empresa.com'
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'tu-email@gmail.com'
  smtp_auth_password: 'tu-app-password'
  smtp_require_tls: true
```

### 3. Crear Usuario

```bash
sudo useradd --no-create-home --shell /bin/false alertmanager
sudo chown -R alertmanager:alertmanager /opt/alertmanager
```

### 4. Verificar

```bash
/opt/alertmanager/alertmanager --config.file=/opt/alertmanager/alertmanager.yml
```

Acceder a: http://localhost:9093

---

## Instalación de Grafana

### 1. Instalar Grafana (Ubuntu/Debian)

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

### 2. Instalar Grafana (CentOS/RHEL)

```bash
cat > /etc/yum.repos.d/grafana.repo << 'EOF'
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF

sudo yum install grafana
```

### 3. Configurar Datasource de Prometheus

Crear archivo `/etc/grafana/provisioning/datasources/prometheus.yml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: false
    jsonData:
      httpMethod: POST
      timeInterval: 15s
```

### 4. Configurar Dashboard Provider

Crear archivo `/etc/grafana/provisioning/dashboards/cics-pa.yml`:

```yaml
apiVersion: 1
providers:
  - name: 'CICS PA Dashboards'
    orgId: 1
    folder: 'CICS PA'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### 5. Copiar Dashboard

```bash
sudo mkdir -p /var/lib/grafana/dashboards
sudo cp /opt/cics-pa/monitoring/grafana/dashboards/cics-pa-backend-dashboard.json \
  /var/lib/grafana/dashboards/
sudo chown -R grafana:grafana /var/lib/grafana/dashboards
```

### 6. Iniciar Grafana

```bash
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```

Acceder a: http://localhost:3000 (admin/admin)

---

## Configuración del Sistema

### 1. Configurar Firewall (si es necesario)

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 9093/tcp  # Alertmanager
sudo ufw allow 3000/tcp  # Grafana

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --permanent --add-port=9093/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

### 2. Configurar ODBC

Editar `/etc/odbc.ini`:

```ini
[DVM_DSN]
Description = DVM Database
Driver = /path/to/odbc/driver
Server = tu-servidor-dvm
Port = 1521
Database = DVM
```

---

## Inicio de Servicios

### Opción 1: Inicio Manual

```bash
# Terminal 1: Backend
cd /opt/cics-pa/cics-pa-backend
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Prometheus
/opt/prometheus/prometheus \
  --config.file=/opt/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.enable-lifecycle

# Terminal 3: Alertmanager
/opt/alertmanager/alertmanager \
  --config.file=/opt/alertmanager/alertmanager.yml \
  --storage.path=/opt/alertmanager/data

# Terminal 4: Grafana (ya iniciado como servicio)
# sudo systemctl status grafana-server
```

### Opción 2: Usar Systemd (Recomendado)

Ver sección siguiente.

---

## Servicios como Systemd

### 1. Servicio para CICS PA Backend

Crear `/etc/systemd/system/cics-pa-backend.service`:

```ini
[Unit]
Description=CICS PA Backend
After=network.target

[Service]
Type=simple
User=cicspa
Group=cicspa
WorkingDirectory=/opt/cics-pa/cics-pa-backend
Environment="PATH=/opt/cics-pa/cics-pa-backend/venv/bin"
ExecStart=/opt/cics-pa/cics-pa-backend/venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Servicio para Prometheus

Crear `/etc/systemd/system/prometheus.service`:

```ini
[Unit]
Description=Prometheus
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/opt/prometheus/prometheus \
  --config.file=/opt/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.enable-lifecycle \
  --storage.tsdb.retention.time=30d
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Servicio para Alertmanager

Crear `/etc/systemd/system/alertmanager.service`:

```ini
[Unit]
Description=Alertmanager
After=network.target

[Service]
Type=simple
User=alertmanager
Group=alertmanager
ExecStart=/opt/alertmanager/alertmanager \
  --config.file=/opt/alertmanager/alertmanager.yml \
  --storage.path=/opt/alertmanager/data
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Crear Usuario cicspa

```bash
sudo useradd --system --no-create-home --shell /bin/false cicspa
sudo chown -R cicspa:cicspa /opt/cics-pa/cics-pa-backend
```

### 5. Habilitar e Iniciar Servicios

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicios
sudo systemctl enable cics-pa-backend
sudo systemctl enable prometheus
sudo systemctl enable alertmanager
sudo systemctl enable grafana-server

# Iniciar servicios
sudo systemctl start cics-pa-backend
sudo systemctl start prometheus
sudo systemctl start alertmanager
sudo systemctl start grafana-server

# Verificar estado
sudo systemctl status cics-pa-backend
sudo systemctl status prometheus
sudo systemctl status alertmanager
sudo systemctl status grafana-server
```

---

## Verificación

### 1. Verificar Backend

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/metrics
```

### 2. Verificar Prometheus

```bash
# Ver targets
curl http://localhost:9090/api/v1/targets

# O acceder via web
firefox http://localhost:9090/targets
```

### 3. Verificar Grafana

```bash
# Acceder via web
firefox http://localhost:3000

# Login: admin / admin
# Ir a Dashboards → Browse → CICS PA
```

### 4. Ver Logs

```bash
# Backend
sudo journalctl -u cics-pa-backend -f

# Prometheus
sudo journalctl -u prometheus -f

# Alertmanager
sudo journalctl -u alertmanager -f

# Grafana
sudo journalctl -u grafana-server -f
```

---

## URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Backend API | http://localhost:8000/docs | - |
| Metrics | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| Grafana | http://localhost:3000 | admin/admin |

---

## Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
sudo journalctl -u cics-pa-backend -n 100 --no-pager

# Verificar ODBC
odbcinst -j
isql -v DVM_DSN

# Verificar puerto
sudo netstat -tlnp | grep 8000
```

### Prometheus no scracea el backend

```bash
# Verificar configuración
/opt/prometheus/promtool check config /opt/prometheus/prometheus.yml

# Verificar conectividad
curl http://localhost:8000/metrics
```

### Grafana no muestra datos

1. Verificar datasource: Configuration → Data Sources → Prometheus → Test
2. Verificar que Prometheus tenga datos
3. Revisar queries en los paneles

---

## Mantenimiento

### Backups

```bash
# Backup de Prometheus
tar czf prometheus-backup-$(date +%Y%m%d).tar.gz /opt/prometheus/data

# Backup de Grafana
tar czf grafana-backup-$(date +%Y%m%d).tar.gz /var/lib/grafana

# Backup de configuración
tar czf config-backup-$(date +%Y%m%d).tar.gz \
  /opt/cics-pa/cics-pa-backend/.env \
  /opt/prometheus/prometheus.yml \
  /opt/alertmanager/alertmanager.yml
```

### Actualización

```bash
# Backend
cd /opt/cics-pa/cics-pa-backend
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart cics-pa-backend

# Prometheus (descargar nueva versión y reemplazar binario)
# Alertmanager (similar a Prometheus)
# Grafana (sudo apt-get upgrade grafana)
```

---

## Seguridad

### Recomendaciones

1. **Cambiar credenciales por defecto** de Grafana
2. **Usar HTTPS** con certificados SSL/TLS
3. **Configurar autenticación** en Prometheus/Alertmanager
4. **Restringir acceso** con firewall
5. **Rotar secrets** de ODBC regularmente
6. **Monitorear logs** de seguridad

---

## Soporte

Para más información, consultar:
- [MONITORING_SETUP.md](./MONITORING_SETUP.md) - Guía detallada de monitoreo
- [README.md](./README.md) - Documentación general

**Versión**: 1.0.0
**Última actualización**: 2025-11-16
