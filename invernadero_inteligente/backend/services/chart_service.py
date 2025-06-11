import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from models.data import DataPoint


class ChartService:
    @staticmethod
    def generate_time_series_chart(dispositivo, tipo_dato, data_points):
        try:
            # Preparar datos
            timestamps = [datetime.strptime(dp.timestamp, "%Y-%m-%d %H:%M:%S") for dp in data_points]
            values = [dp.valor for dp in data_points]

            # Crear gráfica
            plt.figure(figsize=(10, 5))
            plt.plot(timestamps, values, marker='o', linestyle='-')
            plt.title(f"{tipo_dato} para {dispositivo}")
            plt.xlabel("Fecha y Hora")
            plt.ylabel(tipo_dato)
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convertir a imagen base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()

            return image_base64

        except Exception as e:
            print(f"Error generando gráfica: {e}")
            return None