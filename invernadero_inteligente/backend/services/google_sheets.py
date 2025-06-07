import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import GSHEETS_CREDENTIALS, SPREADSHEET_ID

class GoogleSheetsDB:
    def __init__(self):
        if not GSHEETS_CREDENTIALS.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo de credenciales en: {GSHEETS_CREDENTIALS}\n"
                "Pasos para solucionar:\n"
                "1. Descarga el JSON desde Google Cloud Console\n"
                "2. Colócalo en backend/credentials/\n"
                "3. Verifica el nombre del archivo"
            )

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            str(GSHEETS_CREDENTIALS), scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(SPREADSHEET_ID)

    def get_first_sheet_name(self):
        """Prueba mínima de conexión"""
        return self.sheet.sheet1.title