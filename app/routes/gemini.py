"""
Rutas para el procesamiento con Gemini AI
"""
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Form, Body
from fastapi.responses import JSONResponse
import httpx

from app.config import GEMINI_KEY, GEMINI_MODEL
from app.database import supabase_client

router = APIRouter(prefix="/parse", tags=["gemini"])


async def fetch_company_names() -> List[str]:
    """Obtener nombres de empresas de la base de datos"""
    if not supabase_client:
        return []
    try:
        resp = supabase_client.table("companies").select("name").limit(1000).execute()
        data = getattr(resp, "data", None) or []
        return [r.get("name") for r in data if r.get("name")]
    except Exception as e:
        print("[WARN] Error fetching companies:", e)
        return []


def build_prompt(_type: str, text: str, companies_list: Optional[List[str]] = None) -> str:
    """Construir el prompt para Gemini según el tipo de extracción"""
    if _type == "companies":
        return (
            "You are a data extractor. Extract companies mentioned in the following Spanish or English text and return a JSON object with a single top-level key \"items\" whose value is an array of company objects.\n\n"
            "For each company include as many of these fields as you can detect:\n"
            "- name: official company name (string)\n"
            "- country: country or best-guess (string)\n"
            "- sector: industry/sector (string)\n"
            "- total_revenue: numeric or string if available (string)\n"
            "- net_profit: numeric or string if available (string)\n"
            "- lead_status: one of \"lead\", \"prospect\", \"customer\", \"unknown\" if inferable (string)\n"
            "- source: short string saying where it was mentioned (optional)\n"
            "- confidence: number between 0 and 1 (optional)\n\n"
            "Return ONLY valid JSON (no surrounding explanation). Example:\n"
            '{"items":[{"name":"Acme Corp","country":"Peru","sector":"Agritech","lead_status":"lead"}]}\n\n'
            f"Text:\n{text}"
        )

    contexto_empresas = (
        f"Empresas conocidas (para desambiguar si es necesario): {', '.join(companies_list or [])}.\n\n"
        if companies_list
        else ""
    )

    return (
        "Eres un extractor de datos. Extrae contactos individuales del texto (en español o inglés) y devuelve SOLO un objeto JSON válido con una clave de nivel superior \"items\", cuyo valor es un arreglo de contactos.\n\n"
        "REQUISITOS DE CADA CONTACTO (usa estos nombres EXACTOS de campos):\n"
        "- first_name: nombre(s) de pila (string)\n"
        "- last_name: apellido(s) (string)\n"
        "- company: nombre de empresa donde trabaja (string)\n"
        "- cargo: el cargo o función que realiza (string)\n"
        "- email: correo electrónico (string) [opcional, puede omitirse si no está]\n"
        "- telefono: número telefónico en formato local o internacional (string) [opcional, puede omitirse si no está]\n"
        "- country: país (string)\n"
        "- role: SOLO puede ser \"Trabajador\" o \"Director General\". Si el cargo describe al director general/CEO/gerente general, usa \"Director General\"; en caso contrario usa \"Trabajador\".\n\n"
        "RESTRICCIONES:\n"
        "- Devuelve ÚNICAMENTE JSON (sin explicación, sin markdown).\n"
        "- Si un dato no aparece, omite ese campo (no lo dejes vacío).\n"
        "- No inventes correos o teléfonos.\n\n"
        "FORMATO: Devuelve JSON compacto en una sola línea (sin saltos de línea ni espacios innecesarios).\n\n"
        "EJEMPLO DE SALIDA (solo como guía del formato):\n"
        '{"items":[{"first_name":"María","last_name":"Rivas","company":"Andes AgroTech Solutions","cargo":"Gerente de Operaciones","email":"maria@ejemplo.com","country":"Perú","role":"Trabajador"}]}\n\n'
        f"{contexto_empresas}TEXTO:\n{text}"
    )


async def call_gemini(_type: str, text: str) -> JSONResponse:
    """Llamar a la API de Gemini para procesar texto"""
    if not GEMINI_KEY:
        return JSONResponse(
            status_code=200,
            content={
                "ok": False,
                "reason": "no_gemini_key",
                "message": "GEMINI_KEY_API not configured on server",
            },
        )

    try:
        prompt: str
        if _type == "contacts":
            companies = []
            try:
                companies = await fetch_company_names()
            except Exception as e:
                print("[WARN] Could not fetch company names:", e)
            prompt = build_prompt(_type, text, (companies or [])[:200])
        else:
            prompt = build_prompt(_type, text)

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        )
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 2048,
                "temperature": 0.0,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, json=body)

        if r.status_code < 200 or r.status_code >= 300:
            return JSONResponse(
                status_code=502,
                content={
                    "ok": False,
                    "reason": "gemini_error",
                    "status": r.status_code,
                    "body": r.text,
                },
            )

        json_body = r.json()
        parts = (
            json_body.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [])
        )
        content_text = "\n".join([p.get("text", "") for p in parts if p.get("text")])

        if not content_text:
            return JSONResponse(
                status_code=200,
                content={"ok": True, "parsed": None, "raw": json.dumps(json_body)}
            )

        try:
            import re
            m = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", content_text)
            json_text = m.group(0) if m else content_text
            parsed = json.loads(json_text)
            return JSONResponse(status_code=200, content={"ok": True, "parsed": parsed})
        except Exception:
            return JSONResponse(
                status_code=200,
                content={"ok": True, "parsed": None, "raw": content_text}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "reason": "exception",
                "message": str(e),
            },
        )


@router.post("")
async def parse(text: str = Form(None), type: str = Form(None), body: dict = None):
    """Procesar texto con Gemini (genérico)"""
    if body and not text:
        text = body.get("text")
        type = body.get("type")
    if not text:
        raise HTTPException(status_code=400, detail="no text provided")
    _type = "companies" if type == "companies" else "contacts"
    return await call_gemini(_type, text)


@router.post("/contacts")
async def parse_contacts(body: dict = Body(...)):
    """Extraer contactos de texto con Gemini"""
    text = body.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="no text provided")
    return await call_gemini("contacts", text)


@router.post("/companies")
async def parse_companies(body: dict = Body(...)):
    """Extraer empresas de texto con Gemini"""
    text = body.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="no text provided")
    return await call_gemini("companies", text)
