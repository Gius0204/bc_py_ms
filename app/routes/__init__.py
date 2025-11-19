"""
Archivo de inicialización para el módulo de rutas
"""
from fastapi import APIRouter

from app.routes import companies, contacts, calls, emails, gemini

# Crear router principal que agrupa todas las rutas
api_router = APIRouter()

# Incluir los routers de cada módulo
api_router.include_router(companies.router)
api_router.include_router(contacts.router)
api_router.include_router(calls.router)
api_router.include_router(emails.router)
api_router.include_router(gemini.router)
