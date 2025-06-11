# backend/services/google_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import GSHEETS_CREDENTIALS, SPREADSHEET_ID


class GoogleSheetsDB:
    def __init__(self):
        if not GSHEETS_CREDENTIALS.exists():
            raise FileNotFoundError(f"Credenciales no encontradas en: {GSHEETS_CREDENTIALS}")

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            str(GSHEETS_CREDENTIALS), scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(SPREADSHEET_ID)

    def get_worksheet(self, name):
        """Obtiene una hoja por nombre, la crea si no existe"""
        try:
            return self.sheet.worksheet(name)
        except:
            return self.sheet.add_worksheet(name, 100, 10)