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
        """Asocia un dispositivo a un usuario de manera atómica"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")

            # Buscar todas las ocurrencias del número de serie
            cells = worksheet.findall(str(serial_number).strip())

            if not cells:
                raise ValueError(f"Dispositivo {serial_number} no encontrado")

            for cell in cells:
                if cell.col == 1:  # Columna de número de serie
                    # Verificar que no esté ya asignado a otro usuario
                    current_user = worksheet.cell(cell.row, 2).value
                    if current_user and str(current_user).strip().lower() != str(user_email).strip().lower():
                        raise ValueError(f"Dispositivo ya asignado a otro usuario: {current_user}")

                    # Actualizar asignación
                    worksheet.update_cell(cell.row, 2, user_email)  # Usuario Asociado
                    worksheet.update_cell(cell.row, 4, "Asignado")  # Estado
                    return True

            raise ValueError(f"Dispositivo {serial_number} no encontrado en columna 1")

        except Exception as e:
            print(f"Error asociando dispositivo: {e}")
            raise

    @staticmethod
    def obtener_por_serie(serial_number):
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Dispositivos")
        records = worksheet.get_all_records()

        for dispositivo in records:
            if str(dispositivo['Número de Serie']).strip() == str(serial_number).strip():
                return dispositivo
        return None