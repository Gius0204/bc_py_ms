"""
Configuración de la base de datos y dependencias de Supabase
"""
from typing import Optional
from fastapi import HTTPException

try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

# Cliente de Supabase
supabase_client: Optional[Client] = None

if create_client and SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print("[WARN] Could not initialize Supabase client:", e)


def get_supabase() -> Client:
    """
    Dependency para obtener el cliente de Supabase
    """
    if not supabase_client:
        raise HTTPException(
            status_code=500,
            detail="Supabase server client not configured (set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)"
        )
    return supabase_client
