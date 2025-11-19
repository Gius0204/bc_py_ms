# Backend Python - Arquitectura Modular

## Estructura del Proyecto

```
backend-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── config.py            # Configuración de variables de entorno
│   ├── database.py          # Conexión a Supabase
│   ├── models.py            # Modelos Pydantic para validación
│   └── routes/              # Rutas organizadas por entidad
│       ├── __init__.py
│       ├── companies.py     # CRUD de empresas
│       ├── contacts.py      # CRUD de contactos
│       ├── calls.py         # CRUD de llamadas
│       ├── emails.py        # Envío y gestión de emails
│       └── gemini.py        # Procesamiento con IA (Gemini)
├── requirements.txt
└── README.md
```

## Entidades y Modelos

### 1. Companies (Empresas)

**Tabla en Supabase:** `companies`

**Campos:**

- `id`: int (primary key)
- `name`: str (requerido)
- `contacto_principal`: str (opcional)
- `interacciones_hoy`: int (default: 0)
- `ultima_accion`: str (opcional)
- `responsable`: str (opcional)
- `estado`: str (default: "Activo")
- `total_revenue`: float (opcional)
- `net_profit`: float (opcional)
- `country`: str (opcional)
- `sector`: str (opcional)
- `lead_status`: str (default: "No contactada")
- `created_at`: datetime

**Endpoints:**

- `GET /companies` - Listar todas las empresas
- `GET /companies/{id}` - Obtener una empresa
- `POST /companies` - Crear empresa
- `PATCH /companies/{id}` - Actualizar empresa
- `DELETE /companies/{id}` - Eliminar empresa

---

### 2. Contacts (Contactos)

**Tabla en Supabase:** `contacts`

**Campos:**

- `id`: int (primary key)
- `company_id`: int (foreign key a companies)
- `nombre`: str (requerido)
- `cargo`: str (opcional)
- `email`: str (opcional)
- `telefono`: str (opcional)
- `fuente`: str (opcional)
- `propietario`: str (opcional)
- `fecha_creacion`: date (opcional)
- `estado`: str (default: "Nuevo")
- `first_name`: str (opcional)
- `last_name`: str (opcional)
- `country`: str (opcional)
- `role`: str (opcional)
- `created_at`: datetime

**Endpoints:**

- `GET /contacts` - Listar todos los contactos
- `GET /contacts/{id}` - Obtener un contacto
- `POST /contacts` - Crear contacto
- `PATCH /contacts/{id}` - Actualizar contacto
- `DELETE /contacts/{id}` - Eliminar contacto

---

### 3. Calls (Llamadas)

**Tabla en Supabase:** `calls`

**Campos:**

- `id`: int (primary key)
- `contact_id`: int (foreign key a contacts)
- `company_id`: int (foreign key a companies)
- `duracion`: int (opcional)
- `resultado`: str (opcional)
- `siguiente_paso`: str (opcional)
- `responsable`: str (opcional)
- `asunto`: str (opcional)
- `notas`: str (opcional)
- `created_at`: datetime

**Endpoints:**

- `GET /calls` - Listar todas las llamadas
- `GET /calls/{id}` - Obtener una llamada
- `POST /calls` - Crear llamada
- `PATCH /calls/{id}` - Actualizar llamada
- `DELETE /calls/{id}` - Eliminar llamada

---

### 4. Emails (Correos)

**Tabla en Supabase:** `emails`

**Campos:**

- `id`: int (primary key)
- `asunto`: str (requerido)
- `para`: str (opcional)
- `plantilla`: str (opcional)
- `estado`: str (opcional)
- `fecha_hora`: datetime (opcional)
- `responsable`: str (opcional)
- `created_at`: datetime

**Endpoints:**

- `GET /emails/health` - Verificar servicio de email
- `POST /emails/send` - Enviar email (con adjuntos)
- `GET /emails` - Listar todos los emails
- `GET /emails/{id}` - Obtener un email

---

### 5. Gemini AI (Procesamiento de Texto)

**Endpoints:**

- `POST /parse` - Procesar texto genérico
- `POST /parse/contacts` - Extraer contactos de texto
- `POST /parse/companies` - Extraer empresas de texto

**Funcionalidad:**

- Extracción de información de contactos desde texto libre
- Extracción de información de empresas desde texto libre
- Utiliza Gemini AI para procesamiento inteligente
- Contexto de empresas existentes para mejor precisión

---

## Configuración

### Variables de Entorno (.env)

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Gemini AI
GEMINI_KEY_API=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

# Email (Gmail)
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD_APP=your_app_password

# CORS
CORS_ORIGIN=*
```

## Instalación y Ejecución

```bash
# Activar entorno virtual
cd backend-python
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload --port 3000
```

## Arquitectura

### Separación de Responsabilidades

1. **main.py**: Punto de entrada, configuración de FastAPI y CORS
2. **config.py**: Centraliza todas las variables de entorno
3. **database.py**: Maneja la conexión con Supabase
4. **models.py**: Define los schemas Pydantic para validación
5. **routes/**: Cada archivo maneja una entidad específica

### Ventajas de esta Estructura

- ✅ **Modular**: Cada entidad en su propio archivo
- ✅ **Escalable**: Fácil agregar nuevas entidades
- ✅ **Mantenible**: Código organizado y fácil de encontrar
- ✅ **Type-safe**: Validación con Pydantic
- ✅ **Clean Code**: Separación clara de responsabilidades
- ✅ **DRY**: Reutilización de código (database, config)

## API Documentation

Una vez ejecutado el servidor, accede a:

- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc
