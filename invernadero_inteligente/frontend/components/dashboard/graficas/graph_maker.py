import io
import matplotlib.pyplot as plt
import pygame
from datetime import datetime
from invernadero_inteligente.frontend.services.api_service import APIService


def generar_grafica(tipo_dato: str, dispositivo: str, limit: int = 1000, ancho_px: int = 900,
                    alto_px: int = 500) -> pygame.Surface:
    """
    Obtiene los datos desde el backend (/data/raw), genera una gráfica con matplotlib y
    devuelve una Surface de Pygame que puede ser renderizada directamente.
    Muestra todos los puntos históricos con espaciado uniforme, marcando sólo los días únicos en el eje X.
    """
    try:
        # Obtener datos del backend
        response = APIService.obtener_datos_raw(dispositivo=dispositivo, tipo_dato=tipo_dato, limit=limit)

        if response.get("status") != "success" or not response.get("data"):
            return APIService._crear_superficie_error("No se encontraron datos")

        registros = response["data"]

        timestamps = []
        valores = []

        for r in registros:
            raw_fecha = r.get("fecha")
            raw_hora = r.get("hora")
            if not raw_fecha or not raw_hora:
                continue
            try:
                dt = datetime.strptime(f"{raw_fecha} {raw_hora}", "%d/%m/%Y %H:%M:%S")
            except ValueError:
                continue

            timestamps.append(dt)
            valores.append(float(r["valor"]))

        # Validación: mínimo 2 puntos
        if len(timestamps) < 2:
            return APIService._crear_superficie_error("No hay suficientes datos para graficar")

        # Asegurar orden cronológico (más antiguo a más reciente)
        combined = sorted(zip(timestamps, valores), key=lambda x: x[0])
        timestamps, valores = zip(*combined)

        # Crear índices secuenciales para el eje X
        indices_x = list(range(len(timestamps)))

        # Identificar posiciones donde cambia el día para las etiquetas del eje X
        etiquetas_x = []
        posiciones_etiquetas = []
        fecha_anterior = None

        for i, dt in enumerate(timestamps):
            fecha_actual = dt.strftime("%d/%m/%Y")
            if fecha_actual != fecha_anterior:
                etiquetas_x.append(fecha_actual)
                posiciones_etiquetas.append(i)
                fecha_anterior = fecha_actual

        # Ajustar tamaño en pulgadas para matplotlib (1 pulgada ≈ 100 px)
        fig_width = ancho_px / 100
        fig_height = alto_px / 100

        # Crear gráfica
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.plot(indices_x, valores, marker='o', linestyle='-')
        ax.set_title(f"{tipo_dato} - {dispositivo}")
        ax.set_xlabel("Fecha")
        ax.set_ylabel(tipo_dato)
        ax.grid(True)

        # Configurar etiquetas del eje X solo en los cambios de día
        if posiciones_etiquetas:
            ax.set_xticks(posiciones_etiquetas)
            ax.set_xticklabels(etiquetas_x, rotation=45, ha='right')

        fig.tight_layout()

        # Guardar en buffer y convertir a Surface
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)

        return pygame.image.load(buffer).convert_alpha()

    except Exception as e:
        print(f"[GraphMaker] Error al generar gráfica: {e}")
        return APIService._crear_superficie_error("Error generando la gráfica")