# backend/services/chart_service.py
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from models.data import DataPoint
import numpy as np
from typing import List, Dict, Optional


class ChartService:
    @staticmethod
    def generate_time_series_chart(dispositivo: str, tipo_dato: str, data_points: List[DataPoint]) -> Optional[str]:
        """Genera un gráfico de serie temporal en formato base64"""
        try:
            if not data_points:
                return None

            # Preparar datos
            timestamps = [datetime.strptime(dp.timestamp, "%Y-%m-%d %H:%M:%S") for dp in data_points]
            values = [dp.valor for dp in data_points]

            # Crear figura con tamaño adecuado para Pygame
            plt.figure(figsize=(8, 4), dpi=100)

            # Gráfico principal
            plt.plot(timestamps, values, marker='o', linestyle='-', color='#2ecc71', linewidth=2, markersize=5)

            # Personalización
            plt.title(f"{tipo_dato} - {dispositivo}", fontsize=12, pad=10)
            plt.xlabel("Fecha y Hora", fontsize=10)
            plt.ylabel(tipo_dato, fontsize=10)

            # Formato de ejes
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.gcf().autofmt_xdate()  # Formato automático para fechas

            # Ajustar márgenes
            plt.tight_layout()

            # Convertir a imagen base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()

            return image_base64

        except Exception as e:
            print(f"Error generando gráfica: {e}")
            return None

    @staticmethod
    def generate_interactive_chart_data(dispositivo: str, tipo_dato: str, data_points: List[DataPoint]) -> Dict:
        """Prepara datos para gráficos interactivos en Pygame"""
        if not data_points:
            return {}

        # Preparar datos estructurados
        timestamps = [dp.timestamp for dp in data_points]
        values = [dp.valor for dp in data_points]

        # Calcular estadísticas básicas
        min_val = min(values) if values else 0
        max_val = max(values) if values else 0
        avg_val = sum(values) / len(values) if values else 0

        return {
            "dispositivo": dispositivo,
            "tipo_dato": tipo_dato,
            "timestamps": timestamps,
            "values": values,
            "stats": {
                "min": min_val,
                "max": max_val,
                "avg": avg_val,
                "last": values[-1] if values else 0
            }
        }