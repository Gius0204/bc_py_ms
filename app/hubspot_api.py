# hubspot_api.py
import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("CLAVE_API_HUBSPOT")

if not HUBSPOT_TOKEN:
    raise RuntimeError("HUBSPOT_TOKEN no está definido en las variables de entorno")

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}"
}

BASE_URL = "https://api.hubapi.com"

def _hubspot_get_all(object_type: str, properties: str):
    """
    object_type: 'companies' o 'contacts'
    """
    url = f"{BASE_URL}/crm/v3/objects/{object_type}"
    all_items = []
    after = None

    while True:
        params = {
            "limit": 100,
            "properties": properties
        }
        if after:
            params["after"] = after

        r = requests.get(url, headers=HEADERS, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=500,
                                detail=f"Error al obtener {object_type}: {r.status_code} - {r.text}")

        data = r.json()
        all_items.extend(data.get("results", []))

        paging = data.get("paging", {})
        next_page = paging.get("next")
        if next_page and "after" in next_page:
            after = next_page["after"]
        else:
            break

    return all_items


# ------- EMPRESAS --------
def obtener_empresas_simple():
    props = "hs_object_id,name,city,country"
    return _hubspot_get_all("companies", props)


# ------- CONTACTOS --------
def obtener_contactos_simple():
    props = "hs_object_id,email,firstname,lastname,phone"
    return _hubspot_get_all("contacts", props)


# ------- SINCRONIZACIÓN DE EMPRESAS -------
def sincronizar_empresa_a_hubspot(empresa_data: dict):
    """
    Sincroniza una empresa de Supabase a HubSpot.
    Si tiene hubspot_id, actualiza; sino, crea nueva.
    
    Campos sincronizados:
    - name → name
    - country → country
    - total_revenue → annualrevenue
    - net_profit → net_profit (campo personalizado)
    - sector → industry
    - lead_status → hs_lead_status
    """
    hubspot_id = empresa_data.get("hubspot_id")
    
    # Mapeo de campos de Supabase a HubSpot (SOLO los campos especificados)
    properties = {
        "name": empresa_data.get("name", ""),
        "country": empresa_data.get("country", ""),
        "annualrevenue": str(empresa_data.get("total_revenue", "") or ""),
        "industry": empresa_data.get("sector", ""),
        "hs_lead_status": _map_lead_status_to_hubspot_internal(empresa_data.get("lead_status")),
    }
    
    # net_profit como campo personalizado si existe
    if empresa_data.get("net_profit") is not None:
        properties["net_profit"] = str(empresa_data.get("net_profit"))
    
    # Limpiar valores None y vacíos
    properties = {k: v for k, v in properties.items() if v is not None and v != ""}
    
    if hubspot_id:
        # Verificar que el registro existe en HubSpot
        if not _verificar_registro_existe("companies", hubspot_id):
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró la empresa con hs_object_id {hubspot_id} en HubSpot. Sincroniza sin hubspot_id para crear un nuevo registro."
            )
        
        # ACTUALIZAR empresa existente
        url = f"{BASE_URL}/crm/v3/objects/companies/{hubspot_id}"
        payload = {"properties": properties}
        
        r = requests.patch(url, headers=HEADERS, json=payload)
        if r.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Error actualizando empresa en HubSpot: {r.status_code} - {r.text}"
            )
        
        return {
            "hubspot_id": hubspot_id,
            "action": "updated",
            "data": r.json()
        }
    else:
        # CREAR nueva empresa
        url = f"{BASE_URL}/crm/v3/objects/companies"
        payload = {"properties": properties}
        
        r = requests.post(url, headers=HEADERS, json=payload)
        if r.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Error creando empresa en HubSpot: {r.status_code} - {r.text}"
            )
        
        response_data = r.json()
        # Usar hs_object_id como hubspot_id
        new_hubspot_id = response_data.get("properties", {}).get("hs_object_id") or response_data.get("id")
        
        return {
            "hubspot_id": new_hubspot_id,
            "action": "created",
            "data": response_data
        }


# ------- SINCRONIZACIÓN DE CONTACTOS -------
def sincronizar_contacto_a_hubspot(contacto_data: dict, company_hubspot_id: str = None):
    """
    Sincroniza un contacto de Supabase a HubSpot.
    Si tiene hubspot_id, actualiza; sino, crea nuevo.
    
    Campos sincronizados:
    - nombre → firstname + lastname
    - last_name → lastname
    - country → country
    - cargo → jobtitle
    - email → email
    - telefono → phone
    - estado → hs_lead_status (con valores internos de HubSpot)
    """
    hubspot_id = contacto_data.get("hubspot_id")
    
    # Determinar first_name y last_name
    first_name = contacto_data.get("first_name") or contacto_data.get("nombre", "").split()[0] if contacto_data.get("nombre") else ""
    last_name = contacto_data.get("last_name") or " ".join(contacto_data.get("nombre", "").split()[1:]) if contacto_data.get("nombre") else ""
    
    # Mapeo de campos de Supabase a HubSpot (SOLO los campos especificados)
    properties = {
        "firstname": first_name,
        "lastname": last_name,
        "country": contacto_data.get("country", ""),
        "jobtitle": contacto_data.get("cargo", ""),
        "email": contacto_data.get("email", ""),
        "phone": contacto_data.get("telefono", ""),
        "hs_lead_status": _map_lead_status_to_hubspot_internal(contacto_data.get("estado")),
    }
    
    # Limpiar valores None y vacíos
    properties = {k: v for k, v in properties.items() if v is not None and v != ""}
    
    if hubspot_id:
        # Verificar que el registro existe en HubSpot
        if not _verificar_registro_existe("contacts", hubspot_id):
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el contacto con hs_object_id {hubspot_id} en HubSpot. Sincroniza sin hubspot_id para crear un nuevo registro."
            )
        
        # ACTUALIZAR contacto existente
        url = f"{BASE_URL}/crm/v3/objects/contacts/{hubspot_id}"
        payload = {"properties": properties}
        
        r = requests.patch(url, headers=HEADERS, json=payload)
        if r.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Error actualizando contacto en HubSpot: {r.status_code} - {r.text}"
            )
        
        result = {
            "hubspot_id": hubspot_id,
            "action": "updated",
            "data": r.json()
        }
    else:
        # CREAR nuevo contacto
        url = f"{BASE_URL}/crm/v3/objects/contacts"
        payload = {"properties": properties}
        
        r = requests.post(url, headers=HEADERS, json=payload)
        if r.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Error creando contacto en HubSpot: {r.status_code} - {r.text}"
            )
        
        response_data = r.json()
        # Usar hs_object_id como hubspot_id
        new_hubspot_id = response_data.get("properties", {}).get("hs_object_id") or response_data.get("id")
        
        result = {
            "hubspot_id": new_hubspot_id,
            "action": "created",
            "data": response_data
        }
    
    # Si hay company_hubspot_id, asociar el contacto con la empresa
    if company_hubspot_id and result.get("hubspot_id"):
        asociar_contacto_empresa(result["hubspot_id"], company_hubspot_id)
    
    return result


def _map_lead_status_to_hubspot_internal(lead_status: str) -> str:
    """Mapea el lead_status de Supabase a los valores internos de hs_lead_status en HubSpot"""
    mapping = {
        "Nuevo": "NEW",
        "Abierto": "OPEN",
        "En curso": "IN_PROGRESS",
        "Negocio abierto": "OPEN_DEAL",
        "Sin calificar": "UNQUALIFIED",
        "Intento de contacto": "ATTEMPTED_TO_CONTA",
        "Conectado": "CONNECTED",
        "Mal momento": "BAD_TIMING"
    }
    return mapping.get(lead_status, "NEW")


def _verificar_registro_existe(object_type: str, object_id: str) -> bool:
    """Verifica si un registro existe en HubSpot usando su hs_object_id"""
    url = f"{BASE_URL}/crm/v3/objects/{object_type}/{object_id}"
    r = requests.get(url, headers=HEADERS)
    return r.status_code == 200


def asociar_contacto_empresa(contact_hubspot_id: str, company_hubspot_id: str):
    """
    Asocia un contacto con una empresa en HubSpot
    """
    url = f"{BASE_URL}/crm/v4/objects/contacts/{contact_hubspot_id}/associations/companies/{company_hubspot_id}"
    
    # Tipo de asociación: contact_to_company
    payload = [
        {
            "associationCategory": "HUBSPOT_DEFINED",
            "associationTypeId": 279  # contact_to_company
        }
    ]
    
    r = requests.put(url, headers=HEADERS, json=payload)
    if r.status_code not in [200, 201, 204]:
        # No lanzar error, solo registrar
        print(f"Advertencia: No se pudo asociar contacto {contact_hubspot_id} con empresa {company_hubspot_id}: {r.text}")
    
    return r.status_code in [200, 201, 204]
