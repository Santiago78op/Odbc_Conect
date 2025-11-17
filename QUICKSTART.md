# Quick Start - CICS PA Backend con Monitoreo

Guía rápida para iniciar el backend y el stack de monitoreo en 10 minutos.

## 🚀 Instalación Rápida

### 1. Backend CICS PA

```bash
# Ir al directorio del backend
cd cics-pa-backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cat > .env << 'EOF'
APP_NAME=CICS PA Abends Monitor
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# ODBC - AJUSTAR
ODBC_DSN=DVM_DSN
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password
EOF

# Crear directorio de logs
mkdir -p logs

# Iniciar backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend corriendo en: http://localhost:8000/docs

### 2. Prometheus

```bash
# Descargar Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz
cd prometheus-2.48.0.linux-amd64

# Copiar configuración (ajustar ruta según tu instalación)
cp <ruta-al-repo>/monitoring/prometheus.yml .
cp <ruta-al-repo>/monitoring/alert_rules.yml .

# Editar prometheus.yml para apuntar a localhost:8000
sed -i 's/cics-pa-backend:8000/localhost:8000/g' prometheus.yml

# Iniciar Prometheus
./prometheus --config.file=prometheus.yml --storage.tsdb.path=./data
```

✅ Prometheus corriendo en: http://localhost:9090

### 3. Alertmanager (Opcional)

```bash
# Descargar Alertmanager
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
tar xvfz alertmanager-0.26.0.linux-amd64.tar.gz
cd alertmanager-0.26.0.linux-amd64

# Copiar configuración
cp <ruta-al-repo>/monitoring/alertmanager.yml .

# IMPORTANTE: Editar alertmanager.yml y configurar SMTP
nano alertmanager.yml

# Iniciar Alertmanager
./alertmanager --config.file=alertmanager.yml
```

✅ Alertmanager corriendo en: http://localhost:9093

### 4. Grafana

#### Ubuntu/Debian

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Configurar datasource
sudo mkdir -p /etc/grafana/provisioning/datasources
cat | sudo tee /etc/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
EOF

# Copiar dashboard
sudo mkdir -p /var/lib/grafana/dashboards
sudo cp monitoring/grafana/dashboards/cics-pa-backend-dashboard.json /var/lib/grafana/dashboards/

# Iniciar Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### macOS

```bash
brew install grafana
brew services start grafana
```

✅ Grafana corriendo en: http://localhost:3000 (admin/admin)

---

## 🌐 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Backend API** | http://localhost:8000/docs | - |
| **Métricas** | http://localhost:8000/metrics | - |
| **Prometheus** | http://localhost:9090 | - |
| **Alertmanager** | http://localhost:9093 | - |
| **Grafana** | http://localhost:3000 | admin/admin |

---

## ✅ Verificación Rápida

```bash
# 1. Verificar backend
curl http://localhost:8000/api/v1/health

# 2. Verificar métricas
curl http://localhost:8000/metrics | grep cics_pa

# 3. Verificar Prometheus
curl http://localhost:9090/api/v1/targets | jq

# 4. Ver dashboard en Grafana
# Ir a: http://localhost:3000 → Dashboards → Browse → CICS PA
```

---

## 📊 Ver Métricas

### En Prometheus

1. Ir a http://localhost:9090
2. En el query box, ejecutar:

```promql
# Tasa de requests
rate(cics_pa_http_requests_total[5m])

# Latencia p95
histogram_quantile(0.95, sum(rate(cics_pa_http_request_duration_seconds_bucket[5m])) by (le))

# Conexiones ODBC
cics_pa_db_connections_active

# Abends de CICS
rate(cics_pa_abends_total[5m])
```

### En Grafana

1. Ir a http://localhost:3000
2. Login: admin / admin
3. Dashboards → Browse → CICS PA → CICS PA Backend - Monitoreo Completo

---

## 🛑 Detener Todo

```bash
# Backend (Ctrl+C en la terminal)

# Prometheus (Ctrl+C en la terminal)

# Alertmanager (Ctrl+C en la terminal)

# Grafana
sudo systemctl stop grafana-server
```

---

## 📚 Documentación Completa

Para instalación detallada y configuración de servicios systemd:
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) - Guía completa de instalación
- [MONITORING_SETUP.md](./MONITORING_SETUP.md) - Configuración de monitoreo

---

## 🆘 Problemas Comunes

### Backend: Error de conexión ODBC

```bash
# Verificar DSN
odbcinst -j
isql -v DVM_DSN

# Verificar credenciales en .env
cat cics-pa-backend/.env
```

### Prometheus: No scraped backend

```bash
# Verificar que prometheus.yml apunta a localhost:8000
grep "localhost:8000" prometheus.yml

# Verificar que el backend está corriendo
curl http://localhost:8000/metrics
```

### Grafana: No muestra datos

1. Configuration → Data Sources → Prometheus
2. URL debe ser: http://localhost:9090
3. Click en "Save & Test"
4. Si falla, verificar que Prometheus esté corriendo

---

## 🎯 Siguiente Paso

Una vez verificado que todo funciona, configura los servicios como systemd para que se inicien automáticamente. Ver: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md#servicios-como-systemd)

---

**¿Necesitas ayuda?** Consulta la documentación completa o abre un issue.
