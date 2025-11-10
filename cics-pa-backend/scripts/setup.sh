#!/bin/bash
# ==============================================
# Setup script para Linux/Mac
# ==============================================

echo "============================================"
echo "CICS PA Backend - Setup"
echo "============================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar Python
echo -e "${YELLOW}[1/6] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
echo ""

# 2. Crear entorno virtual
echo -e "${YELLOW}[2/6] Creando entorno virtual...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Entorno virtual ya existe, saltando...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
fi
echo ""

# 3. Activar entorno virtual
echo -e "${YELLOW}[3/6] Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# 4. Actualizar pip
echo -e "${YELLOW}[4/6] Actualizando pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip actualizado${NC}"
echo ""

# 5. Instalar dependencias
echo -e "${YELLOW}[5/6] Instalando dependencias...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# 6. Configurar .env
echo -e "${YELLOW}[6/6] Configurando .env...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}.env ya existe, saltando...${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env creado desde .env.example${NC}"
    echo -e "${YELLOW}⚠ Edita .env con tu configuración ODBC${NC}"
fi
echo ""

# Crear directorio de logs
mkdir -p logs

echo "============================================"
echo -e "${GREEN}Setup completado!${NC}"
echo "============================================"
echo ""
echo "Próximos pasos:"
echo "1. Edita .env con tu configuración ODBC"
echo "2. Activa el entorno virtual: source venv/bin/activate"
echo "3. Ejecuta: python -m src.main"
echo ""
