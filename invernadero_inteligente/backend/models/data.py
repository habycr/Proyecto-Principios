from datetime import datetime
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB


class DataPoint:
    def __init__(self, timestamp, dispositivo, tipo_dato, valor):
        self.timestamp = timestamp
        self.dispositivo = dispositivo
        self.tipo_dato = tipo_dato
        self.valor = float(valor) if valor else 0.0

    @classmethod
    def get_by_device_and_type(cls, dispositivo, tipo_dato, limit=100):
        """Obtiene datos históricos para un dispositivo y tipo específico"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Datos")
            records = worksheet.get_all_records()

            filtered_data = [
                DataPoint(
                    timestamp=record['Timestamp'],
                    dispositivo=record['Dispositivo'],
                    tipo_dato=record['TipoDato'],
                    valor=record['Valor']
                )
                for record in records
                if str(record['Dispositivo']).strip() == dispositivo
                   and str(record['TipoDato']).strip().lower() == tipo_dato.lower()
            ]

            # Ordenar por timestamp y limitar resultados
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            return filtered_data[:limit]

        except Exception as e:
            print(f"Error obteniendo datos: {e}")
            return []

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "dispositivo": self.dispositivo,
            "tipo_dato": self.tipo_dato,
            "valor": self.valor
        }