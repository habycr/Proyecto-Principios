from datetime import datetime
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


class DataPoint:
    def __init__(self, timestamp, dispositivo, tipo_dato, valor):
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

    @classmethod
    def get_by_device_and_type(cls, dispositivo, tipo_dato, limit=1000):
        """Obtiene datos históricos para un dispositivo y tipo específico"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Datos")
            records = worksheet.get_all_records()

            filtered_data = []
            for record in records:
                if (
                    str(record.get("Dispositivo", "")).strip() == dispositivo
                    and str(record.get("TipoDato", "")).strip().lower() == tipo_dato.lower()
                ):
                    fecha = record.get("Fecha")
                    hora = record.get("Hora")
                    if fecha and hora:
                        timestamp_str = f"{fecha} {hora}"
                        try:
                            dp = DataPoint(
                                timestamp=timestamp_str,
                                dispositivo=record.get("Dispositivo"),
                                tipo_dato=record.get("TipoDato"),
                                valor=record.get("Valor")
                            )
                            filtered_data.append(dp)
                        except Exception as e:
                            print(f"Error procesando registro: {e}")

            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            return filtered_data[:limit]

        except Exception as e:
            print(f"Error obteniendo datos: {e}")
            return []

    def to_dict(self):
        return {
            "fecha": self.timestamp.strftime("%d/%m/%Y"),
            "hora": self.timestamp.strftime("%H:%M:%S"),
            "dispositivo": self.dispositivo,
            "tipo_dato": self.tipo_dato,
            "valor": self.valor
        }
