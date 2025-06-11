from backend.services.google_sheets import GoogleSheetsDB


class Device:
    @staticmethod
    def exists(serial_number):
        """Verifica si el número de serie existe en la hoja"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")
            records = worksheet.get_all_records()

            # Buscar el número de serie en la primera columna
            for device in records:
                if str(device['Número de Serie']).strip() == str(serial_number).strip():
                    return True
            return False
        except Exception as e:
            print(f"Error verificando dispositivo: {e}")
            return False

    @staticmethod
    def is_available(serial_number):
        """Verifica si el dispositivo está disponible (sin usuario asociado)"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")
            records = worksheet.get_all_records()

            for device in records:
                if str(device['Número de Serie']).strip() == str(serial_number).strip():
                    return not bool(device.get('Usuario Asociado', '').strip())
            return False
        except Exception as e:
            print(f"Error verificando disponibilidad: {e}")
            return False

    @staticmethod
    def associate_to_user(serial_number, user_email):

        """Asocia un dispositivo a un usuario"""
        print(f"Asociando dispositivo {serial_number} a {user_email}")  # Debug
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Dispositivos")

        # Si es hoja nueva, crear encabezados
        if len(worksheet.get_all_values()) == 0:
            worksheet.append_row(["Número de Serie", "Usuario Asociado", "Modelo", "Estado"])

        # Buscar la fila del dispositivo y actualizar
        cells = worksheet.findall(str(serial_number))
        for cell in cells:
            if cell.col == 1:  # Columna de número de serie
                worksheet.update_cell(cell.row, 2, user_email)  # Columna Usuario Asociado
                worksheet.update_cell(cell.row, 4, "Asignado")  # Actualizar estado
                return True

        raise ValueError(f"Dispositivo {serial_number} no encontrado")

    @staticmethod
    def obtener_por_serie(serial_number):
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Dispositivos")
        records = worksheet.get_all_records()

        for dispositivo in records:
            if str(dispositivo['Número de Serie']).strip() == str(serial_number).strip():
                return dispositivo
        return None