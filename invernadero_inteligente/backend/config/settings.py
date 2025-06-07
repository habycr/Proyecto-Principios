# backend/config/settings.py
from pathlib import Path

# 1. Directorios
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_DIR = BASE_DIR / "credentials"

# 2. Google Sheets - ¡REEMPLAZA ESTOS VALORES!
GSHEETS_CREDENTIALS = CREDENTIALS_DIR / "google_sheets.json"  # Ruta exacta al JSON
SPREADSHEET_ID = "1YxZ4E-lidhnCogh3G2gTST8ONTm6_9JV7zYbQh7z4Ms"  # Ejemplo: 44 caracteres
