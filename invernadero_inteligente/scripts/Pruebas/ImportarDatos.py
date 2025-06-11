from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


def print_dispositivo_DISP1234():
    try:
        # Conectar con Google Sheets
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Datos")

        # Obtener todos los registros
        records = worksheet.get_all_records()

        # Filtrar solo los registros de DISP1234
        disp1234_data = [record for record in records if str(record.get('Dispositivo', '')).strip() == 'DISP1234']

        # Imprimir los datos de forma legible
        print("\nDatos del dispositivo DISP1234:")
        print("-" * 60)
        print(f"{'Timestamp':<20} | {'TipoDato':<12} | {'Valor':<10}")
        print("-" * 60)

        for record in disp1234_data:
            print(
                f"{record.get('Timestamp', ''):<20} | {record.get('TipoDato', ''):<12} | {record.get('Valor', ''):<10}")

        print("-" * 60)
        print(f"Total de registros encontrados: {len(disp1234_data)}")

    except Exception as e:
        print(f"Error al obtener datos: {e}")


# Llamar a la función
print_dispositivo_DISP1234()