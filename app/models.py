"""
Modelos Pydantic para validación de datos
Basados en la estructura de las tablas de Supabase
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field


# ============ Companies Models ============
class CompanyBase(BaseModel):
    name: str
    contacto_principal: Optional[str] = None
    interacciones_hoy: Optional[int] = 0
    ultima_accion: Optional[str] = None
    responsable: Optional[str] = None
    estado: Optional[str] = "Activo"
    total_revenue: Optional[float] = None
    net_profit: Optional[float] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    lead_status: Optional[str] = "No contactada"


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    contacto_principal: Optional[str] = None
    interacciones_hoy: Optional[int] = None
    ultima_accion: Optional[str] = None
    responsable: Optional[str] = None
    estado: Optional[str] = None
    total_revenue: Optional[float] = None
    net_profit: Optional[float] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    lead_status: Optional[str] = None


class Company(CompanyBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Contacts Models ============
class ContactBase(BaseModel):
    company_id: Optional[int] = None
    nombre: str
    cargo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = None
    propietario: Optional[str] = None
    fecha_creacion: Optional[date] = None
    estado: Optional[str] = "Nuevo"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    company_id: Optional[int] = None
    nombre: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = None
    propietario: Optional[str] = None
    fecha_creacion: Optional[date] = None
    estado: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None


class Contact(ContactBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Calls Models ============
class CallBase(BaseModel):
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    duracion: Optional[int] = None
    resultado: Optional[str] = None
    siguiente_paso: Optional[str] = None
    responsable: Optional[str] = None
    asunto: Optional[str] = None
    notas: Optional[str] = None


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    duracion: Optional[int] = None
    resultado: Optional[str] = None
    siguiente_paso: Optional[str] = None
    responsable: Optional[str] = None
    asunto: Optional[str] = None
    notas: Optional[str] = None


class Call(CallBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Emails Models ============
class EmailBase(BaseModel):
    asunto: str
    para: Optional[str] = None
    plantilla: Optional[str] = None
    estado: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    responsable: Optional[str] = None


class EmailCreate(EmailBase):
    pass


class EmailUpdate(BaseModel):
    asunto: Optional[str] = None
    para: Optional[str] = None
    plantilla: Optional[str] = None
    estado: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    responsable: Optional[str] = None


class Email(EmailBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Gemini Parse Models ============
class ParseRequest(BaseModel):
    text: str
    type: Optional[str] = "contacts"


class ParseResponse(BaseModel):
    ok: bool
    parsed: Optional[dict] = None
    raw: Optional[str] = None
    reason: Optional[str] = None
    message: Optional[str] = None


# ============ Email Send Models ============
class EmailSendRequest(BaseModel):
    asunto: str
    para: str
    plantilla: Optional[str] = None
    body: Optional[str] = ""
    responsable: Optional[str] = None
