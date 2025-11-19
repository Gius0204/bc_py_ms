"""
API principal de instrategy-sales-flow
Organizado con arquitectura modular
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.config import ALLOWED_ORIGINS, CORS_ORIGIN
from app.routes import api_router

from app.hubspot_api import (
    obtener_empresas_simple, 
    obtener_contactos_simple,
    sincronizar_empresa_a_hubspot,
    sincronizar_contacto_a_hubspot
)

# Crear aplicación FastAPI
app = FastAPI(title="instrategy-sales-flow API (Python)")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todas las rutas
app.include_router(api_router)

@app.get("/empresas")
def listar_empresas():
    return obtener_empresas_simple()

@app.get("/contactos")
def listar_contactos():
    return obtener_contactos_simple()


# ------- MODELOS PARA SINCRONIZACIÓN -------
class EmpresaSyncRequest(BaseModel):
    id: int
    name: str
    country: Optional[str] = None
    sector: Optional[str] = None
    lead_status: Optional[str] = None
    total_revenue: Optional[float] = None
    net_profit: Optional[float] = None
    hubspot_id: Optional[str] = None


class ContactoSyncRequest(BaseModel):
    id: int
    nombre: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    country: Optional[str] = None
    estado: Optional[str] = None
    company_id: Optional[int] = None
    hubspot_id: Optional[str] = None


# ------- ENDPOINTS DE SINCRONIZACIÓN -------
@app.post("/sync/empresa")
async def sincronizar_empresa(empresa: EmpresaSyncRequest):
    """
    Sincroniza una empresa de Supabase a HubSpot.
    Retorna el hubspot_id para actualizar en Supabase.
    """
    try:
        resultado = sincronizar_empresa_a_hubspot(empresa.dict())
        return {
            "success": True,
            "hubspot_id": resultado["hubspot_id"],
            "action": resultado["action"],
            "message": f"Empresa {resultado['action']} en HubSpot exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/contacto")
async def sincronizar_contacto(contacto: ContactoSyncRequest, company_hubspot_id: Optional[str] = None):
    """
    Sincroniza un contacto de Supabase a HubSpot.
    Opcionalmente asocia con una empresa usando company_hubspot_id.
    Retorna el hubspot_id para actualizar en Supabase.
    """
    try:
        resultado = sincronizar_contacto_a_hubspot(contacto.dict(), company_hubspot_id)
        return {
            "success": True,
            "hubspot_id": resultado["hubspot_id"],
            "action": resultado["action"],
            "message": f"Contacto {resultado['action']} en HubSpot exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint raíz
@app.get("/")
async def root():
    return {
        "message": "instrategy-sales-flow API (Python)",
        "version": "2.0",
        "endpoints": {
            "companies": "/companies",
            "contacts": "/contacts",
            "calls": "/calls",
            "emails": "/emails",
            "parse": "/parse"
        }
    }
