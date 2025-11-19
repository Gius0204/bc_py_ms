# API CRUD — estructuras de tablas

Este archivo documenta los endpoints CRUD específicos añadidos en `app/main.py` y la estructura esperada (campos y tipos) para las tablas principales detectadas en la base de datos Supabase.

Endpoints por tabla (todos requieren que el backend tenga `SUPABASE_SERVICE_ROLE_KEY` configurado):

- `GET /<table>`: lista con filtros por query params (ej.: `?company_id=1&limit=50`).
- `GET /<table>/{id}`: obtener registro por id.
- `POST /<table>`: insertar uno o varios objetos (array o objeto único).
- `PATCH /<table>/{id}`: actualizar campos del registro {id}.
- `DELETE /<table>/{id}`: eliminar registro por id.

Tablas detectadas y estructura (tipos según DB):

## companies

- id: integer (PK, generado automáticamente al insertar)
- name: text
- contacto_principal: text (nullable)
- interacciones_hoy: integer (nullable, default 0)
- ultima_accion: text (nullable)
- responsable: text (nullable)
- estado: text (nullable, default 'Activo')
- created_at: timestamptz (default now())
- total_revenue: real (nullable)
- net_profit: real (nullable)
- country: text (nullable)
- sector: text (nullable)
- lead_status: text (nullable, default 'No contactada')

Ejemplo `POST /companies` (crear una empresa):

```
{
  "name": "TechCorp S.A.",
  "contacto_principal": "María González",
  "country": "Perú",
  "sector": "Tecnología",
  "lead_status": "No contactada",
  "responsable": "juan@empresa.com"
}
```

Ejemplo `PATCH /companies/12` (actualizar):

```
{
  "ultima_accion": "Email enviado",
  "interacciones_hoy": 3
}
```

## contacts

- id: integer (PK)
- company_id: integer (FK -> companies.id) (nullable)
- nombre: text
- cargo: text (nullable)
- email: text (nullable)
- telefono: text (nullable)
- fuente: text (nullable)
- propietario: text (nullable)
- fecha_creacion: date (nullable)
- estado: text (nullable, default 'Nuevo')
- created_at: timestamptz (default now())
- first_name: text (nullable)
- last_name: text (nullable)
- country: text (nullable)
- role: text (nullable)

Ejemplo `POST /contacts` (crear contacto):

```
{
  "company_id": 5,
  "nombre": "Ana Martínez",
  "cargo": "Directora General",
  "email": "ana.martinez@empresa.com",
  "telefono": "+52123456789",
  "fuente": "Prospección AI",
  "propietario": "juan@empresa.com",
  "fecha_creacion": "2025-11-19",
  "first_name": "Ana",
  "last_name": "Martínez",
  "country": "México",
  "role": "Director General"
}
```

Nota: `company_id` puede omitirse si el contacto aún no está asociado; puedes crear la empresa primero y luego actualizar el contacto.

## calls

- id: integer (PK)
- contact_id: integer (FK -> contacts.id) (nullable)
- company_id: integer (FK -> companies.id) (nullable)
- duracion: integer (segundos) (nullable)
- resultado: text (nullable)
- siguiente_paso: text (nullable)
- responsable: text (nullable)
- created_at: timestamptz (default now())
- asunto: text (nullable)
- notas: text (nullable)

Ejemplo `POST /calls` (crear registro de llamada):

```
{
  "contact_id": 7,
  "company_id": 5,
  "duracion": 180,
  "resultado": "Interesado",
  "siguiente_paso": "Enviar demo",
  "responsable": "juan@empresa.com",
  "asunto": "Llamada inicial",
  "notas": "Agendar demo la próxima semana"
}
```

## emails

- id: integer (PK)
- asunto: text
- para: text (lista separada por comas en un solo string)
- plantilla: text (nullable)
- estado: text (nullable)
- fecha_hora: timestamptz (nullable)
- responsable: text (nullable)
- created_at: timestamptz (default now())

Nota: los registros en la tabla `emails` se crean únicamente desde el backend cuando se envía un correo mediante `POST /email/send`.
No existe un endpoint público `POST /emails` ni operaciones `PATCH` o `DELETE` para `emails` — solo están disponibles:

- `GET /emails` — listar (con filtros simples)
- `GET /emails/{id}` — obtener por id

Si necesitas insertar registros manualmente por razones administrativas o migraciones, hazlo directamente desde el panel de Supabase o mediante una tarea administrativa segura en el backend.

--

Notas finales:

- Usa `GET /<table>?<campo>=<valor>` para filtrar con igualdad simple (ej.: `GET /contacts?company_id=5`).
- `POST /<table>` acepta tanto un objeto JSON (registro) como un arreglo de objetos para inserciones masivas.
- `PATCH /<table>/{id}` espera un objeto con los campos a actualizar.
- Asegúrate de no exponer la `SUPABASE_SERVICE_ROLE_KEY` en el frontend; el backend debe ejecutarse con esa variable en el entorno.

Si quieres, actualizo el frontend para que use estos endpoints explícitos en lugar del genérico `/db/{table}`.
