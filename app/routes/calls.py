"""
Rutas para el manejo de llamadas (calls)
"""
from typing import Any
from fastapi import APIRouter, HTTPException, Path, Query, Request, Body, Depends

from app.models import Call, CallCreate, CallUpdate
from app.database import get_supabase
from supabase import Client

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("")
async def get_all_calls(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    db: Client = Depends(get_supabase)
):
    """Obtener todas las llamadas con filtros opcionales"""
    try:
        query = db.table("calls").select("*")
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


@router.get("/{call_id}")
async def get_call(
    call_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Obtener una llamada por ID"""
    try:
        resp = db.table("calls").select("*").eq("id", call_id).limit(1).execute()
        data = getattr(resp, "data", None) or []
        if not data:
            raise HTTPException(status_code=404, detail="Call not found")
        return {"ok": True, "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_call(
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Crear una nueva llamada"""
    try:
        resp = db.table("calls").insert(payload).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{call_id}")
async def update_call(
    call_id: int = Path(...),
    payload: Any = Body(...),
    db: Client = Depends(get_supabase)
):
    """Actualizar una llamada existente"""
    try:
        resp = db.table("calls").update(payload).eq("id", call_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{call_id}")
async def delete_call(
    call_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Eliminar una llamada"""
    try:
        resp = db.table("calls").delete().eq("id", call_id).execute()
        return {"ok": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
