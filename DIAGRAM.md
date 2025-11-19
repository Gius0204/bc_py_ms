# Diagrama de Arquitectura - Backend Python

## Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│              (Frontend React/Vite)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP Request
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      MAIN.PY                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FastAPI App + CORS Middleware                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Route to Module
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   ROUTES (API Router)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Companies │  │Contacts  │  │  Calls   │  │ Emails   │   │
│  │  .py     │  │  .py     │  │  .py     │  │  .py     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐                                               │
│  │ Gemini   │  (Procesamiento IA)                          │
│  │  .py     │                                               │
│  └──────────┘                                               │
└──────┬───────────────────┬───────────────────┬──────────────┘
       │                   │                   │
       │ Uses Models       │ Uses Database     │ Uses Config
       ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────────┐   ┌─────────────┐
│  MODELS.PY  │   │   DATABASE.PY   │   │  CONFIG.PY  │
│             │   │                 │   │             │
│ Pydantic    │   │ Supabase Client │   │ Environment │
│ Schemas     │   │ get_supabase()  │   │ Variables   │
└─────────────┘   └────────┬────────┘   └─────────────┘
                           │
                           │ Connects to
                           ▼
                  ┌─────────────────┐
                  │    SUPABASE     │
                  │                 │
                  │ ┌─────────────┐ │
                  │ │  companies  │ │
                  │ │  contacts   │ │
                  │ │  calls      │ │
                  │ │  emails     │ │
                  │ └─────────────┘ │
                  └─────────────────┘
```

## Estructura de Archivos

```
backend-python/
│
├── app/
│   │
│   ├── main.py ────────────────► Punto de entrada
│   │                              • Crea FastAPI app
│   │                              • Configura CORS
│   │                              • Incluye routers
│   │
│   ├── config.py ─────────────► Configuración
│   │                              • SUPABASE_URL
│   │                              • GEMINI_KEY
│   │                              • GMAIL credentials
│   │
│   ├── database.py ───────────► Conexión DB
│   │                              • Cliente Supabase
│   │                              • Dependency injection
│   │
│   ├── models.py ─────────────► Validación
│   │                              • CompanyCreate/Update
│   │                              • ContactCreate/Update
│   │                              • CallCreate/Update
│   │                              • EmailCreate/Update
│   │
│   └── routes/ ───────────────► Endpoints
│       │
│       ├── __init__.py ───────► Router principal
│       │
│       ├── companies.py ──────► CRUD Empresas
│       │                          GET, POST, PATCH, DELETE
│       │
│       ├── contacts.py ───────► CRUD Contactos
│       │                          GET, POST, PATCH, DELETE
│       │
│       ├── calls.py ──────────► CRUD Llamadas
│       │                          GET, POST, PATCH, DELETE
│       │
│       ├── emails.py ─────────► Emails
│       │                          send, health, GET
│       │
│       └── gemini.py ─────────► IA Processing
│                                  parse, parse/contacts,
│                                  parse/companies
│
├── env/ ──────────────────────► Virtual Environment
├── requirements.txt
└── README.md
```

## Patrones de Diseño Utilizados

### 1. **Dependency Injection**

```python
# database.py
def get_supabase() -> Client:
    if not supabase_client:
        raise HTTPException(...)
    return supabase_client

# routes/companies.py
@router.get("")
async def get_all_companies(
    db: Client = Depends(get_supabase)  # ✓ Injection
):
    ...
```

### 2. **Repository Pattern**

Cada archivo en `routes/` actúa como un repositorio para su entidad.

### 3. **Single Responsibility Principle**

- `main.py`: Solo configuración de app
- `config.py`: Solo variables de entorno
- `database.py`: Solo conexión a DB
- `models.py`: Solo definición de schemas
- `routes/*.py`: Solo endpoints de su entidad

### 4. **DRY (Don't Repeat Yourself)**

- Configuración centralizada en `config.py`
- Cliente de DB reutilizable en `database.py`
- Modelos compartidos en `models.py`

## Flujo de Request Típico

```
1. Cliente hace request: POST /companies
   ↓
2. main.py recibe y rutea a companies.router
   ↓
3. companies.py maneja el endpoint
   ↓
4. Valida datos con models.CompanyCreate
   ↓
5. Obtiene DB client con get_supabase()
   ↓
6. Ejecuta operación en Supabase
   ↓
7. Retorna respuesta al cliente
```

## Ventajas de Esta Arquitectura

✅ **Escalabilidad**: Agregar nuevas entidades es simple
✅ **Mantenibilidad**: Código organizado y fácil de navegar
✅ **Testabilidad**: Cada módulo se puede probar independientemente
✅ **Reutilización**: Config, DB y Models compartidos
✅ **Type Safety**: Validación con Pydantic
✅ **Clean Code**: Separación clara de responsabilidades
