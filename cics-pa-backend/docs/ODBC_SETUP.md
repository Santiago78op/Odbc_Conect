# Configuración ODBC para DVM

Esta guía explica cómo configurar ODBC para conectarse a DVM desde el backend.

## ¿Qué es ODBC?

**ODBC** (Open Database Connectivity) es un estándar para conectarse a bases de datos. Necesitas:

1. **Driver ODBC** - Software que implementa el protocolo
2. **DSN** (Data Source Name) - Configuración de conexión
3. **pyodbc** - Librería Python para usar ODBC

## Configuración por Sistema Operativo

### Linux

#### 1. Instalar unixODBC

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install unixodbc unixodbc-dev
```

**RedHat/CentOS:**
```bash
sudo yum install unixODBC unixODBC-devel
```

#### 2. Instalar driver para tu base de datos

**Para DB2:**
```bash
# Descargar IBM Data Server Driver
# Seguir instrucciones de IBM
```

**Para PostgreSQL:**
```bash
sudo apt-get install odbc-postgresql
```

**Para MySQL:**
```bash
sudo apt-get install libmyodbc
```

#### 3. Configurar DSN

Edita `/etc/odbc.ini` (para todo el sistema) o `~/.odbc.ini` (solo tu usuario):

```ini
[DVM_DSN]
Description = DVM Database Connection
Driver = DB2
Database = DVMDB
Servername = dvm-server.company.com
Port = 50000
Protocol = TCPIP
UID = tu_usuario
PWD = tu_password
```

#### 4. Verificar drivers disponibles

```bash
odbcinst -q -d
```

#### 5. Probar conexión

```bash
isql DVM_DSN tu_usuario tu_password
```

Si conecta, verás el prompt `SQL>`.

### Windows

#### 1. El driver ODBC generalmente ya está instalado

Windows incluye controladores ODBC básicos. Para bases de datos específicas:

- **DB2**: Instalar IBM Data Server Client
- **SQL Server**: Ya incluido en Windows
- **Oracle**: Instalar Oracle Client

#### 2. Configurar DSN

**Opción A: Interfaz gráfica**

1. Buscar "ODBC Data Sources" en el menú Start
2. Ir a pestaña "System DSN" o "User DSN"
3. Click "Add..."
4. Seleccionar el driver (ej: IBM DB2 ODBC DRIVER)
5. Configurar:
   - **Data source name**: DVM_DSN
   - **Database**: DVMDB
   - **Server**: dvm-server.company.com
   - **Port**: 50000
6. Click "Test Connection"

**Opción B: Línea de comandos**

Crear archivo `dvm_dsn.reg`:

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\ODBC\ODBC.INI\DVM_DSN]
"Driver"="C:\\Program Files\\IBM\\SQLLIB\\BIN\\db2cli64.dll"
"Database"="DVMDB"
"Servername"="dvm-server.company.com"
"Port"="50000"
```

Importar: `regedit dvm_dsn.reg`

#### 3. Verificar

```cmd
# PowerShell
Get-OdbcDsn

# O en Python
python -c "import pyodbc; print(pyodbc.dataSources())"
```

### macOS

#### 1. Instalar unixODBC

```bash
brew install unixodbc
```

#### 2. Instalar driver

```bash
# Ejemplo para PostgreSQL
brew install psqlodbc
```

#### 3. Configurar igual que Linux

Editar `~/.odbc.ini` y `~/.odbcinst.ini`

## Configuración Específica para DVM

### Si DVM usa DB2

```ini
[DVM_DSN]
Description = CICS PA DVM Database
Driver = IBM DB2 ODBC DRIVER
Database = DVMDB
Hostname = dvm-mainframe.company.com
Port = 50000
Protocol = TCPIP
```

### Si DVM usa SQL Server

```ini
[DVM_DSN]
Description = CICS PA DVM Database
Driver = ODBC Driver 17 for SQL Server
Server = dvm-server.company.com,1433
Database = DVMDB
TrustServerCertificate = yes
```

### Si DVM usa Oracle

```ini
[DVM_DSN]
Description = CICS PA DVM Database
Driver = Oracle 19 ODBC driver
DBQ = //oracle-server:1521/DVMDB
```

## Autenticación

### Opción 1: Credenciales en DSN (no recomendado)

```ini
[DVM_DSN]
...
UID = usuario
PWD = password
```

### Opción 2: Credenciales en .env (recomendado)

DSN sin credenciales:
```ini
[DVM_DSN]
Driver = DB2
Database = DVMDB
Hostname = dvm-server
```

`.env` con credenciales:
```env
ODBC_DSN=DVM_DSN
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password
```

### Opción 3: Autenticación integrada

Algunos sistemas permiten autenticación del usuario actual:

```ini
[DVM_DSN]
...
Trusted_Connection = Yes
```

## Verificar Configuración

### Desde Python

```python
import pyodbc

# Ver drivers disponibles
print(pyodbc.drivers())

# Ver DSNs
print(pyodbc.dataSources())

# Probar conexión
conn = pyodbc.connect('DSN=DVM_DSN;UID=usuario;PWD=password')
cursor = conn.cursor()
cursor.execute("SELECT 1")
print(cursor.fetchone())
conn.close()
```

### Script de prueba

Crea `test_odbc.py`:

```python
#!/usr/bin/env python3
import pyodbc
import sys

dsn = "DVM_DSN"
user = "tu_usuario"
password = "tu_password"

try:
    print(f"Conectando a {dsn}...")
    conn = pyodbc.connect(f'DSN={dsn};UID={user};PWD={password}')
    print("✓ Conexión exitosa")

    cursor = conn.cursor()
    cursor.execute("SELECT 1 AS test")
    result = cursor.fetchone()
    print(f"✓ Query exitosa: {result}")

    conn.close()
    print("✓ Todo funciona correctamente")

except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
```

Ejecutar:
```bash
python test_odbc.py
```

## Troubleshooting

### Error: "Data source name not found"

**Causa**: DSN no configurado

**Solución**:
```bash
# Linux/Mac
cat ~/.odbc.ini
odbcinst -q -s

# Windows
Get-OdbcDsn  # PowerShell
```

### Error: "Driver not found"

**Causa**: Driver ODBC no instalado

**Solución**: Instalar el driver apropiado para tu base de datos

### Error: "Connection timeout"

**Causa**: No puede alcanzar el servidor

**Solución**:
- Verificar hostname/IP
- Verificar puerto
- Verificar firewall
- Ping al servidor

### Error: "Login failed"

**Causa**: Credenciales incorrectas

**Solución**:
- Verificar usuario y password
- Verificar permisos en la base de datos

## Configuración del Backend

Una vez configurado ODBC, edita `.env`:

```env
# DSN configurado
ODBC_DSN=DVM_DSN

# Credenciales
ODBC_USER=tu_usuario
ODBC_PASSWORD=tu_password

# Timeouts (opcional)
ODBC_CONNECTION_TIMEOUT=30
ODBC_QUERY_TIMEOUT=300

# Pool (opcional)
POOL_SIZE=5
MAX_OVERFLOW=10
```

## Recursos Adicionales

- [unixODBC Documentation](http://www.unixodbc.org/)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [Microsoft ODBC Documentation](https://docs.microsoft.com/en-us/sql/odbc/)

## Contacto con TI

Si no tienes acceso a DVM, contacta a tu equipo de TI con esta información:

- **Necesito**: Configurar conexión ODBC a DVM
- **Para**: Sistema de monitoreo de abends CICS PA
- **Requiero**:
  - Hostname/IP del servidor DVM
  - Puerto
  - Nombre de la base de datos
  - Credenciales con acceso de lectura
  - Driver ODBC recomendado
  - Nombre de la tabla de abends (ej: CICS_ABENDS)
