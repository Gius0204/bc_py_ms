"""
Rutas para el manejo de empresas (companies)
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Path, Query, Request, Body, Depends

from app.models import Company, CompanyCreate, CompanyUpdate
from app.database import get_supabase
from supabase import Client

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
async def get_all_companies(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    db: Client = Depends(get_supabase)
):
    """Obtener todas las empresas con filtros opcionales"""
    try:
        query = db.table("companies").select("*")
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


@router.get("/{company_id}")
async def get_company(
    company_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Obtener una empresa por ID"""
    try:
        resp = db.table("companies").select("*").eq("id", company_id).limit(1).execute()
        data = getattr(resp, "data", None) or []
        if not data:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"ok": True, "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_company(
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Crear una nueva empresa"""
    try:
        resp = db.table("companies").insert(payload).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{company_id}")
async def update_company(
    company_id: int = Path(...),
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Actualizar una empresa existente"""
    try:
        resp = db.table("companies").update(payload).eq("id", company_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{company_id}")
async def delete_company(
    company_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Eliminar una empresa"""
    try:
        resp = db.table("companies").delete().eq("id", company_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
