from services.google_sheets import GoogleSheetsDB
from config.settings import SPREADSHEET_ID


def test_connection():
    try:
        print("🔍 Iniciando prueba de conexión...")
        db = GoogleSheetsDB()

        # 1. Obtener la hoja "Usuarios"
        worksheet = db.sheet.worksheet("Usuarios")

        # 2. Leer todos los registros
        records = worksheet.get_all_records()

        if not records:
            print("\nℹ️ La hoja 'Usuarios' está vacía")
            return

        # 3. Mostrar el primer usuario
        first_user = records[0]
        print("\n✅ Conexión exitosa! Datos del primer usuario:")
        print(f"Nombre: {first_user.get('Nombre', 'Columna no encontrada')}")
        print(f"Email: {first_user.get('Email', 'Columna no encontrada')}")
        print(f"Rol: {first_user.get('Rol', 'Columna no encontrada')}")

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        if "WorksheetNotFound" in str(e):
            print("Solución: Crea una hoja llamada 'Usuarios' con las columnas: Nombre, Email, Rol")


if __name__ == "__main__":
    test_connection()