from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


class Device:
    @staticmethod
    def exists(serial_number):
        """
        Verifica si un dispositivo existe en Google Sheets

        Args:
            serial_number: Número de serie del dispositivo

        Returns:
            bool: True si el dispositivo existe, False en caso contrario
        """
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")

            # Buscar el dispositivo por número de serie
            cells = worksheet.findall(str(serial_number).strip())

            # Verificar si alguna celda encontrada está en la columna 1 (Número de Serie)
            for cell in cells:
                if cell.col == 1:  # Columna de número de serie
                    return True

            return False

        except Exception as e:
            print(f"Error verificando existencia del dispositivo: {e}")
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

    @staticmethod
    def actualizar_alertas(serial_number, alertas_config):
        """
        Actualiza las columnas de alertas para un dispositivo específico

        Args:
            serial_number: Número de serie del dispositivo
            alertas_config: Diccionario con la configuración de alertas
        """
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")

            # Buscar el dispositivo por número de serie
            cells = worksheet.findall(str(serial_number).strip())

            if not cells:
                raise ValueError(f"Dispositivo {serial_number} no encontrado")

            device_row = None
            for cell in cells:
                if cell.col == 1:  # Columna de número de serie
                    device_row = cell.row
                    break

            if not device_row:
                raise ValueError(f"Dispositivo {serial_number} no encontrado en columna 1")

            # Obtener encabezados para mapear las columnas correctamente
            headers = worksheet.row_values(1)

            # Mapeo de nombres de alertas a columnas
            column_mapping = {
                'temperatura': {
                    'min': 'Alerta_Temperatura_min',
                    'max': 'Alerta_Temperatura_max'
                },
                'humedad_suelo': {
                    'min': 'Alerta_Humedad_Suelo_min',
                    'max': 'Alerta_Humedad_Suelo_max'
                },
                'humedad_ambiente': {
                    'min': 'Alerta_Humedad_Ambiente_min',
                    'max': 'Alerta_Humedad_Ambiente_max'
                },
                'nivel_drenaje': 'Alerta_Nivel_Agua_Drenaje',
                'nivel_bomba': 'Alerta_Nivel_Agua_Bomba'
            }

            alertas = alertas_config.get('alertas', {})

            # Actualizar cada tipo de alerta
            for alert_type, columns in column_mapping.items():
                if alert_type in alertas:
                    if isinstance(columns, dict):  # Para alertas con min/max
                        for sub_type, col_name in columns.items():
                            if sub_type in alertas[alert_type]:
                                col_idx = headers.index(col_name) + 1  # +1 porque las columnas empiezan en 1
                                worksheet.update_cell(device_row, col_idx, str(alertas[alert_type][sub_type]))
                    else:  # Para alertas simples (nivel)
                        col_idx = headers.index(columns) + 1
                        worksheet.update_cell(device_row, col_idx, str(alertas[alert_type]))

            return True

        except Exception as e:
            print(f"Error actualizando alertas del dispositivo: {e}")
            raise

    @staticmethod
    def obtener_alertas(serial_number):
        """
        Obtiene la configuración de alertas de un dispositivo

        Args:
            serial_number: Número de serie del dispositivo

        Returns:
            Diccionario con la configuración de alertas o None si no se encuentra
        """
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Dispositivos")
            records = worksheet.get_all_records()

            for dispositivo in records:
                if str(dispositivo['Número de Serie']).strip() == str(serial_number).strip():
                    # Extraer y parsear las alertas
                    alertas_config = {}

                    # Parsear temperatura (formato: "min-max")
                    temp_value = dispositivo.get('Alerta_Temperatura', '')
                    if temp_value and '-' in str(temp_value):
                        temp_parts = str(temp_value).split('-')
                        if len(temp_parts) == 2:
                            alertas_config['temperatura'] = {
                                'min': temp_parts[0].strip(),
                                'max': temp_parts[1].strip()
                            }

                    # Parsear humedad del suelo (formato: "min-max")
                    hum_suelo_value = dispositivo.get('Alerta_Humedad_Suelo', '')
                    if hum_suelo_value and '-' in str(hum_suelo_value):
                        hum_suelo_parts = str(hum_suelo_value).split('-')
                        if len(hum_suelo_parts) == 2:
                            alertas_config['humedad_suelo'] = {
                                'min': hum_suelo_parts[0].strip(),
                                'max': hum_suelo_parts[1].strip()
                            }

                    # Parsear humedad ambiente (formato: "min-max")
                    hum_amb_value = dispositivo.get('Alerta_Humedad_Ambiente', '')
                    if hum_amb_value and '-' in str(hum_amb_value):
                        hum_amb_parts = str(hum_amb_value).split('-')
                        if len(hum_amb_parts) == 2:
                            alertas_config['humedad_ambiente'] = {
                                'min': hum_amb_parts[0].strip(),
                                'max': hum_amb_parts[1].strip()
                            }

                    # Nivel de agua drenaje
                    nivel_drenaje = dispositivo.get('Alerta_Nivel_Agua_Drenaje', '')
                    if nivel_drenaje:
                        alertas_config['nivel_drenaje'] = str(nivel_drenaje).strip()

                    # Nivel de agua bomba
                    nivel_bomba = dispositivo.get('Alerta_Nivel_Agua_Bomba', '')
                    if nivel_bomba:
                        alertas_config['nivel_bomba'] = str(nivel_bomba).strip()

                    return alertas_config

            return None

        except Exception as e:
            print(f"Error obteniendo alertas del dispositivo: {e}")
            return None