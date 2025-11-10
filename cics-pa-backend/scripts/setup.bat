@echo off
REM ==============================================
REM Setup script para Windows
REM ==============================================

echo ============================================
echo CICS PA Backend - Setup
echo ============================================
echo.

REM 1. Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no esta instalado
    pause
    exit /b 1
)
python --version
echo.

REM 2. Crear entorno virtual
echo [2/6] Creando entorno virtual...
if exist venv (
    echo Entorno virtual ya existe, saltando...
) else (
    python -m venv venv
    echo Entorno virtual creado
)
echo.

REM 3. Activar entorno virtual
echo [3/6] Activando entorno virtual...
call venv\Scripts\activate.bat
echo Entorno virtual activado
echo.

REM 4. Actualizar pip
echo [4/6] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo Pip actualizado
echo.

REM 5. Instalar dependencias
echo [5/6] Instalando dependencias...
pip install -r requirements.txt --quiet
echo Dependencias instaladas
echo.

REM 6. Configurar .env
echo [6/6] Configurando .env...
if exist .env (
    echo .env ya existe, saltando...
) else (
    copy .env.example .env
    echo .env creado desde .env.example
    echo ADVERTENCIA: Edita .env con tu configuracion ODBC
)
echo.

REM Crear directorio de logs
if not exist logs mkdir logs

echo ============================================
echo Setup completado!
echo ============================================
echo.
echo Proximos pasos:
echo 1. Edita .env con tu configuracion ODBC
echo 2. Activa el entorno virtual: venv\Scripts\activate
echo 3. Ejecuta: python -m src.main
echo.
pause
