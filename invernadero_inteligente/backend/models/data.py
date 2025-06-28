from datetime import datetime
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


class DataPoint:
    def __init__(self, timestamp, dispositivo, tipo_dato, valor, estado_techo=0):
        if isinstance(timestamp, str):
            try:
                self.timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S")
            except:
                self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
        self.dispositivo = dispositivo
        self.tipo_dato = tipo_dato
        self.valor = float(valor) if valor else 0.0
        self.estado_techo = int(estado_techo) if estado_techo else 0

    @classmethod
    def get_by_device_and_type(cls, dispositivo, tipo_dato, limit=1000, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos históricos para un dispositivo y tipo específico con filtro opcional de fechas

        Args:
            dispositivo: Número de serie del dispositivo
            tipo_dato: Tipo de sensor
            limit: Límite de registros a retornar
            fecha_inicio: Fecha de inicio en formato "DD/MM/YYYY" (opcional)
            fecha_fin: Fecha de fin en formato "DD/MM/YYYY" (opcional)
        """
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Datos")
            records = worksheet.get_all_records()

            # Convertir fechas de filtro a objetos datetime si se proporcionan
            fecha_inicio_dt = None
            fecha_fin_dt = None

            if fecha_inicio:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d/%m/%Y")
                    print(f"Filtrando desde: {fecha_inicio_dt}")
                except ValueError as e:
                    print(f"Error parseando fecha_inicio '{fecha_inicio}': {e}")

            if fecha_fin:
                try:
                    # Agregar 23:59:59 para incluir todo el día final
                    fecha_fin_dt = datetime.strptime(fecha_fin, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
                    print(f"Filtrando hasta: {fecha_fin_dt}")
                except ValueError as e:
                    print(f"Error parseando fecha_fin '{fecha_fin}': {e}")

            filtered_data = []
            registros_procesados = 0
            registros_filtrados = 0

            for record in records:
                registros_procesados += 1

                # Filtrar por dispositivo y tipo de dato
                if (
                        str(record.get("Dispositivo", "")).strip() == dispositivo
                        and str(record.get("TipoDato", "")).strip().lower() == tipo_dato.lower()
                ):
                    fecha = record.get("Fecha")
                    hora = record.get("Hora")

                    if fecha and hora:
                        timestamp_str = f"{fecha} {hora}"
                        try:
                            # Crear el DataPoint temporalmente para obtener el timestamp
                            temp_timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")

                            # Aplicar filtros de fecha si se especificaron
                            incluir_registro = True

                            if fecha_inicio_dt and temp_timestamp < fecha_inicio_dt:
                                incluir_registro = False

                            if fecha_fin_dt and temp_timestamp > fecha_fin_dt:
                                incluir_registro = False

                            if incluir_registro:
                                dp = DataPoint(
                                    timestamp=timestamp_str,
                                    dispositivo=record.get("Dispositivo"),
                                    tipo_dato=record.get("TipoDato"),
                                    valor=record.get("Valor"),
                                    estado_techo=record.get("EstadoTecho", 0)
                                )
                                filtered_data.append(dp)
                                registros_filtrados += 1

                        except Exception as e:
                            print(f"Error procesando registro: {e}")

            print(f"Registros procesados: {registros_procesados}")
            print(f"Registros que coinciden con filtros: {registros_filtrados}")

            # Ordenar por fecha (más recientes primero)
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)

            # Aplicar límite
            result = filtered_data[:limit]

            print(f"Registros retornados después del límite: {len(result)}")

            if result:
                print(f"Rango de fechas en resultado: {result[-1].timestamp} a {result[0].timestamp}")

            return result

        except Exception as e:
            print(f"Error obteniendo datos: {e}")
            return []

    @classmethod
    def get_filtered_data(cls, dispositivo=None, tipo_dato=None, fecha_inicio=None, fecha_fin=None, limit=1000):
        """
        Método más genérico para obtener datos con filtros opcionales

        Args:
            dispositivo: Número de serie del dispositivo (opcional)
            tipo_dato: Tipo de sensor (opcional)
            fecha_inicio: Fecha de inicio en formato "DD/MM/YYYY" (opcional)
            fecha_fin: Fecha de fin en formato "DD/MM/YYYY" (opcional)
            limit: Límite de registros a retornar
        """
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Datos")
            records = worksheet.get_all_records()

            # Convertir fechas de filtro a objetos datetime si se proporcionan
            fecha_inicio_dt = None
            fecha_fin_dt = None

            if fecha_inicio:
                try:
                    fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d/%m/%Y")
                except ValueError as e:
                    print(f"Error parseando fecha_inicio '{fecha_inicio}': {e}")

            if fecha_fin:
                try:
                    fecha_fin_dt = datetime.strptime(fecha_fin, "%d/%m/%Y").replace(hour=23, minute=59, second=59)
                except ValueError as e:
                    print(f"Error parseando fecha_fin '{fecha_fin}': {e}")

            filtered_data = []

            for record in records:
                # Aplicar filtros
                incluir_registro = True

                # Filtrar por dispositivo si se especifica
                if dispositivo and str(record.get("Dispositivo", "")).strip() != dispositivo:
                    incluir_registro = False

                # Filtrar por tipo de dato si se especifica
                if tipo_dato and str(record.get("TipoDato", "")).strip().lower() != tipo_dato.lower():
                    incluir_registro = False

                if incluir_registro:
                    fecha = record.get("Fecha")
                    hora = record.get("Hora")

                    if fecha and hora:
                        timestamp_str = f"{fecha} {hora}"
                        try:
                            temp_timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")

                            # Aplicar filtros de fecha
                            if fecha_inicio_dt and temp_timestamp < fecha_inicio_dt:
                                incluir_registro = False

                            if fecha_fin_dt and temp_timestamp > fecha_fin_dt:
                                incluir_registro = False

                            if incluir_registro:
                                dp = DataPoint(
                                    timestamp=timestamp_str,
                                    dispositivo=record.get("Dispositivo"),
                                    tipo_dato=record.get("TipoDato"),
                                    valor=record.get("Valor"),
                                    estado_techo=record.get("EstadoTecho", 0)
                                )
                                filtered_data.append(dp)

                        except Exception as e:
                            print(f"Error procesando registro: {e}")

            # Ordenar por fecha (más recientes primero)
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            return filtered_data[:limit]

        except Exception as e:
            print(f"Error obteniendo datos filtrados: {e}")
            return []

    def to_dict(self):
        return {
            "fecha": self.timestamp.strftime("%d/%m/%Y"),
            "hora": self.timestamp.strftime("%H:%M:%S"),
            "dispositivo": self.dispositivo,
            "tipo_dato": self.tipo_dato,
            "valor": self.valor,
            "estado_techo": self.estado_techo
        }