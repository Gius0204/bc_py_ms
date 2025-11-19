"""
Rutas para el manejo de emails
"""
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Path, Query, Request, Body, Depends, UploadFile, File, Form
import smtplib
from email.message import EmailMessage

from app.models import Email
from app.database import get_supabase
from app.config import GMAIL_USER, GMAIL_PASSWORD_APP
from supabase import Client

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/health")
async def email_health():
    """Verificar estado del servicio de email"""
    return {"ok": True}


@router.post("/send")
async def send_email(
    asunto: str = Form(...),
    para: str = Form(...),
    plantilla: Optional[str] = Form(None),
    body: Optional[str] = Form(""),
    responsable: Optional[str] = Form(None),
    files: List[UploadFile] = File(default_factory=list),
    db: Client = Depends(get_supabase)
):
    """Enviar un email y registrarlo en la base de datos"""
    if not GMAIL_USER or not GMAIL_PASSWORD_APP:
        raise HTTPException(
            status_code=500,
            detail="GMAIL_USER or GMAIL_PASSWORD_APP not configured"
        )

    recipients = [s.strip() for s in str(para).split(",") if s.strip()]
    if not recipients:
        raise HTTPException(status_code=400, detail="Invalid 'para' recipients")

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = asunto
    msg.set_content(body or "")

    # Adjuntar archivos
    for f in files or []:
        try:
            content = await f.read()
            maintype = "application"
            subtype = "octet-stream"
            filename = f.filename or "attachment"
            msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
        except Exception:
            pass

    # Enviar email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD_APP)
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Registrar en la base de datos
    db_result: Optional[dict] = None
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        row = {
            "asunto": asunto,
            "para": ", ".join(recipients),
            "plantilla": plantilla,
            "estado": "enviado",
            "fecha_hora": now_iso,
            "responsable": responsable,
        }
        resp = db.table("emails").insert(row).execute()
        db_result = {"inserted": True, "data": getattr(resp, "data", None)}
    except Exception as e:
        db_result = {"inserted": False, "error": str(e)}

    return {
        "success": True,
        "ok": True,
        "info": {"accepted": recipients, "messageId": msg.get("Message-Id")},
        "db": db_result
    }


@router.get("")
async def get_all_emails(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    db: Client = Depends(get_supabase)
):
    """Obtener todos los emails con filtros opcionales"""
    try:
        query = db.table("emails").select("*")
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


@router.get("/{email_id}")
async def get_email(
    email_id: int = Path(...),
    db: Client = Depends(get_supabase)
):
    """Obtener un email por ID"""
    try:
        resp = db.table("emails").select("*").eq("id", email_id).limit(1).execute()
        data = getattr(resp, "data", None) or []
        if not data:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"ok": True, "data": data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
