# CICS PA Frontend - Monitor de Abends

Frontend web para el monitoreo de **abends** (abnormal endings) en regiones CICS, conectándose al backend FastAPI.

## Stack Tecnológico

- **React 19** - Biblioteca UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **TanStack Query (React Query)** - Manejo de estado del servidor
- **Axios** - Cliente HTTP
- **OpenAPI TypeScript Codegen** - Generación automática de cliente API

## Características

- ✅ Integración total con el backend FastAPI mediante tipos TypeScript generados automáticamente
- ✅ Búsqueda y filtrado de abends por región, programa y límite
- ✅ Tabla responsiva con datos en tiempo real
- ✅ Indicador de estado de conexión con el backend
- ✅ Gestión automática de cache con React Query
- ✅ Manejo de errores y estados de carga
- ✅ Interfaz limpia y moderna

## Estructura del Proyecto

```
cics-pa-frontend/
├── src/
│   ├── api/
│   │   └── generated/        # Cliente generado desde OpenAPI (auto-generado)
│   ├── components/           # Componentes React reutilizables
│   │   ├── Layout/           # Layout principal
│   │   ├── Loading/          # Componente de carga
│   │   ├── ErrorMessage/     # Manejo de errores
│   │   └── AbendsTable/      # Tabla de abends
│   ├── pages/                # Páginas de la aplicación
│   │   └── Dashboard.tsx     # Dashboard principal
│   ├── hooks/                # Custom hooks
│   │   └── useApi.ts         # Hooks para llamadas API
│   ├── services/             # Servicios
│   │   └── api.service.ts    # Cliente API con Axios
│   ├── types/                # Tipos TypeScript
│   │   └── api.types.ts      # Tipos de la API
│   ├── config/               # Configuración
│   │   └── api.config.ts     # Configuración de API
│   ├── providers/            # Providers de contexto
│   │   └── QueryProvider.tsx # Provider de React Query
│   ├── App.tsx               # Componente principal
│   ├── main.tsx              # Punto de entrada
│   └── index.css             # Estilos globales
├── public/                   # Archivos estáticos
├── .env.example              # Variables de entorno de ejemplo
├── package.json              # Dependencias
├── tsconfig.json             # Configuración TypeScript
├── vite.config.ts            # Configuración Vite
└── README.md                 # Este archivo
```

## Instalación

### 1. Instalar dependencias

```bash
cd cics-pa-frontend
npm install
```

### 2. Configurar variables de entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` y configura la URL del backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. (Opcional) Generar cliente desde OpenAPI

Si el backend está corriendo, puedes generar el cliente TypeScript automáticamente:

```bash
# Asegúrate de que el backend esté corriendo en http://localhost:8000
npm run generate:api
```

Esto generará el cliente en `src/api/generated/` con tipos 100% sincronizados con tu backend.

## Uso

### Modo desarrollo

```bash
npm run dev
```

La aplicación iniciará en `http://localhost:5173`

### Build para producción

```bash
npm run build
```

Los archivos se generarán en el directorio `dist/`

### Preview del build

```bash
npm run preview
```

### Linter

```bash
npm run lint
```

## Flujo de Trabajo con OpenAPI

Este proyecto está configurado para generar automáticamente el cliente TypeScript desde la especificación OpenAPI del backend:

1. **Backend FastAPI** expone `/openapi.json` con la especificación completa
2. **Ejecutas** `npm run generate:api`
3. Se genera el cliente en `src/api/generated/` con:
   - Todos los tipos TypeScript de los modelos Pydantic
   - Funciones tipadas para cada endpoint
   - Configuración de Axios integrada

### Ejemplo de uso del cliente generado:

```typescript
// Antes de generar el cliente, usar hooks personalizados:
import { useAbends } from './hooks/useApi';

function MyComponent() {
  const { data, isLoading } = useAbends({
    region: 'PROD01',
    limit: 100
  });

  // 'data' está totalmente tipado
}
```

## Hooks Personalizados

El proyecto incluye hooks de React Query listos para usar:

### `useHealth()`
```typescript
import { useHealth } from './hooks/useApi';

const { data, isLoading, error } = useHealth();
// data: HealthResponse
```

### `useAbends(filters, options)`
```typescript
import { useAbends } from './hooks/useApi';

const { data, isLoading, refetch } = useAbends({
  region: 'PROD01',
  program: 'PAYROLL',
  limit: 50
});
// data: AbendsResponse
```

### `useAbendsSummary(region, options)`
```typescript
import { useAbendsSummary } from './hooks/useApi';

const { data } = useAbendsSummary('PROD01');
// data: AbendsSummaryResponse con estadísticas
```

### `useExecuteQuery()`
```typescript
import { useExecuteQuery } from './hooks/useApi';

const mutation = useExecuteQuery();

mutation.mutate({
  query: 'SELECT * FROM CICS_ABENDS WHERE CICS_REGION = ?',
  params: ['PROD01'],
  fetch_all: true
});
```

### `useTableInfo(tableName, options)`
```typescript
import { useTableInfo } from './hooks/useApi';

const { data } = useTableInfo('CICS_ABENDS');
// data: TableInfoResponse con columnas y metadata
```

## Componentes

### Layout
```typescript
import { Layout } from './components';

<Layout>
  {/* Tu contenido aquí */}
</Layout>
```

### Loading
```typescript
import { Loading } from './components';

<Loading message="Cargando datos..." />
```

### ErrorMessage
```typescript
import { ErrorMessage } from './components';

<ErrorMessage
  message="Error al cargar"
  details={error.message}
  onRetry={() => refetch()}
/>
```

### AbendsTable
```typescript
import { AbendsTable } from './components/AbendsTable/AbendsTable';

<AbendsTable />
// Incluye filtros, búsqueda y tabla responsiva
```

## Configuración de la API

La configuración de la API está en `src/config/api.config.ts`:

```typescript
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};
```

## Tipos TypeScript

Todos los tipos están definidos en `src/types/api.types.ts` y coinciden con los modelos Pydantic del backend:

- `QueryRequest`
- `AbendsFilterRequest`
- `QueryResponse`
- `AbendRecord`
- `AbendsResponse`
- `HealthResponse`
- `ErrorResponse`
- Y más...

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Inicia el servidor de desarrollo |
| `npm run build` | Genera el build de producción |
| `npm run preview` | Preview del build de producción |
| `npm run lint` | Ejecuta el linter |
| `npm run generate:api` | Genera el cliente desde OpenAPI |

## Integración con el Backend

Asegúrate de que el backend FastAPI esté corriendo antes de iniciar el frontend:

```bash
# Terminal 1 - Backend
cd cics-pa-backend
python -m src.main

# Terminal 2 - Frontend
cd cics-pa-frontend
npm run dev
```

El frontend se conectará automáticamente al backend en `http://localhost:8000`

## Personalización

### Cambiar colores

Los colores principales están definidos en los archivos CSS de cada componente. Para cambiar el tema:

1. **Header**: `src/components/Layout/Layout.css` (línea 8)
2. **Botones**: Busca `#667eea` y `#764ba2` en los archivos CSS
3. **Estados**: `src/pages/Dashboard.css`

### Agregar nuevas páginas

1. Crea un nuevo archivo en `src/pages/MiPagina.tsx`
2. Importa y usa en `App.tsx`
3. (Opcional) Instala React Router para múltiples rutas

### Agregar nuevos endpoints

1. Actualiza `src/types/api.types.ts` con los nuevos tipos
2. Crea un nuevo hook en `src/hooks/useApi.ts`
3. Usa el hook en tu componente

## Buenas Prácticas Implementadas

- ✅ Separación de concerns (componentes, hooks, servicios)
- ✅ Tipos TypeScript en todo el código
- ✅ Custom hooks para lógica reutilizable
- ✅ Manejo centralizado de errores
- ✅ Cache y refetch inteligente con React Query
- ✅ Componentes reutilizables
- ✅ Configuración centralizada
- ✅ Variables de entorno para diferentes ambientes

## Próximos Pasos Recomendados

1. **React Router** - Para múltiples páginas y navegación
2. **React Hook Form** - Para formularios complejos
3. **Recharts o Chart.js** - Para gráficos y visualizaciones
4. **TailwindCSS** - Para estilos más rápidos (opcional)
5. **Vitest** - Para testing de componentes
6. **ESLint + Prettier** - Para formateo automático

## Troubleshooting

### Error de CORS

Si ves errores de CORS, verifica que el backend tenga configurado correctamente el middleware:

```python
# En src/main.py del backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error al generar cliente

Si `npm run generate:api` falla:

1. Verifica que el backend esté corriendo
2. Verifica que la URL en el comando sea correcta
3. Verifica que `/openapi.json` sea accesible

### Puerto en uso

Si el puerto 5173 está ocupado, Vite automáticamente usará el siguiente disponible (5174, 5175, etc.)

## Licencia

MIT

## Contacto

Para dudas o sugerencias sobre el frontend, revisa la documentación del backend o abre un issue.
