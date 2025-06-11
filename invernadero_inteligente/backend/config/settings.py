# backend/config/settings.py
from pathlib import Path

# 1. Directorios
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"

# 2. Google Sheets - ¡REEMPLAZA ESTOS VALORES!
GSHEETS_CREDENTIALS = CREDENTIALS_DIR / "google_sheets.json"  # Ruta exacta al JSON
SPREADSHEET_ID = "1YxZ4E-lidhnCogh3G2gTST8ONTm6_9JV7zYbQh7z4Ms"  # Tu ID actual

# 3. Seguridad
PASSWORD_SALT = "INVERNADERO_INTELIGENTE_2025_SALT_SECRET"  # Cambia esto por tu propio salt

# 4. Configuración del servidor
SERVER_HOST = "localhost"
SERVER_PORT = 5000
DEBUG_MODE = True

# 5. CORS (si necesitas acceso desde otros dominios)
CORS_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*"]

# 6. Configuración de validación
MIN_PASSWORD_LENGTH = 8
MIN_SERIAL_LENGTH = 5