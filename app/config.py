"""
Configuración de variables de entorno y conexión a servicios externos
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY_API")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_SERVICE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")
)

# Email Configuration
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD_APP = os.getenv("GMAIL_PASSWORD_APP")

# CORS Configuration
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    CORS_ORIGIN
]
