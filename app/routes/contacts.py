"""
Rutas para el manejo de contactos (contacts)
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Path, Query, Request, Body, Depends

from app.models import Contact, ContactCreate, ContactUpdate
from app.database import get_supabase
from supabase import Client

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def get_all_contacts(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    db: Client = Depends(get_supabase)
):
    """Obtener todos los contactos con filtros opcionales"""
    try:
        query = db.table("contacts").select("*")
        params = dict(request.query_params)
        
        for k, v in params.items():
            if k in {"limit"}:
                continue
            val = v
            try:
                if v is not None and v != "":
                    if "." in v:
                        val = float(v)
                    else:
                        val = int(v)
            except Exception:
                val = v
            query = query.eq(k, val)
        
        resp = query.limit(limit).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}")
async def get_contact(
    contact_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Obtener un contacto por ID"""
    try:
        resp = db.table("contacts").select("*").eq("id", contact_id).limit(1).execute()
        data = getattr(resp, "data", None) or []
        if not data:
            raise HTTPException(status_code=404, detail="Contact not found")
        return {"ok": True, "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_contact(
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Crear un nuevo contacto"""
    try:
        resp = db.table("contacts").insert(payload).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{contact_id}")
async def update_contact(
    contact_id: int = Path(...),
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Actualizar un contacto existente"""
    try:
        resp = db.table("contacts").update(payload).eq("id", contact_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Eliminar un contacto"""
    try:
        resp = db.table("contacts").delete().eq("id", contact_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
