# frontend/components/dashboard/graficas/chart_component.py
import pygame
import base64
import io
from PIL import Image
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.services.api_service import APIService


class ChartComponent:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.chart_surface = None
        self.chart_data = None
        self.hover_index = None
        self.scale_x = 1.0
        self.offset_x = 0
        self.dragging = False
        self.last_mouse_x = 0
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

    def load_data_from_sheet(self, dispositivo: str, tipo_dato: str, days: int = 7):
        """Carga datos desde Google Sheets y los prepara para el gráfico"""
        # Calcular fecha de inicio (hoy - días)
        fecha_inicio = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Obtener datos de la API
        response = APIService.obtener_datos_hoja(
            dispositivo=dispositivo,
            tipo_dato=tipo_dato,
            fecha_inicio=fecha_inicio
        )

        if response.get('status') != 'success':
            print(f"Error al obtener datos: {response.get('message', 'Error desconocido')}")
            return False

        raw_data = response.get('data', [])
        if not raw_data:
            print("No se encontraron datos para los parámetros especificados")
            return False

        # Procesar los datos
        timestamps = []
        values = []

        for row in raw_data:
            try:
                # Asumimos que la estructura es: Timestamp, Dispositivo, TipoDato, Valor
                timestamp_str = row[0]  # Primera columna: Timestamp
                valor = float(row[3])  # Cuarta columna: Valor

                # Convertir timestamp a formato más legible
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamps.append(timestamp.strftime('%d/%m %H:%M'))
                values.append(valor)
            except (IndexError, ValueError) as e:
                print(f"Error procesando fila: {row}. Error: {e}")
                continue

        if not values:
            print("No se pudieron procesar datos válidos")
            return False

        # Calcular estadísticas básicas
        stats = {
            'last': values[-1],
            'max': max(values),
            'min': min(values),
            'avg': sum(values) / len(values)
        }

        # Configurar datos del gráfico
        self.set_chart_data({
            'timestamps': timestamps,
            'values': values,
            'stats': stats,
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato
        })

        return True

    def load_chart_from_base64(self, base64_str: str):
        """Carga un gráfico desde una cadena base64"""
        try:
            # Decodificar la imagen base64
            image_data = base64.b64decode(base64_str.split(',')[1])
            image = Image.open(io.BytesIO(image_data))

            # Convertir a superficie de Pygame
            mode = image.mode
            size = image.size
            data = image.tobytes()

            if mode == "RGB":
                self.chart_surface = pygame.image.fromstring(data, size, "RGB")
            elif mode == "RGBA":
                self.chart_surface = pygame.image.fromstring(data, size, "RGBA")
            else:
                # Convertir a RGB si tiene otro formato
                image = image.convert("RGB")
                data = image.tobytes()
                self.chart_surface = pygame.image.fromstring(data, size, "RGB")

            # Escalar al tamaño del componente
            self.chart_surface = pygame.transform.scale(
                self.chart_surface,
                (self.rect.width, self.rect.height)
            )

            return True
        except Exception as e:
            print(f"Error loading chart image: {e}")
            return False

    def set_chart_data(self, data: Dict):
        """Establece los datos del gráfico para visualización interactiva"""
        self.chart_data = {
            'timestamps': data.get('timestamps', []),
            'values': data.get('values', []),
            'stats': data.get('stats', {
                'last': 0,
                'max': 0,
                'min': 0,
                'avg': 0
            }),
            'dispositivo': data.get('dispositivo', ''),
            'tipo_dato': data.get('tipo_dato', '')
        }
        self.scale_x = 1.0
        self.offset_x = 0
        self.hover_index = None

    def draw(self, surface: pygame.Surface):
        """Dibuja el componente en la superficie dada"""
        # Fondo del gráfico
        pygame.draw.rect(surface, (255, 255, 255), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)

        # Dibujar gráfico si está disponible
        if self.chart_surface:
            surface.blit(self.chart_surface, self.rect)

        # Dibujar datos interactivos si existen
        if self.chart_data:
            self._draw_interactive_chart(surface)

        # Dibujar información de hover si existe
        if self.hover_index is not None and self.chart_data:
            self._draw_hover_info(surface)

    def _draw_interactive_chart(self, surface: pygame.Surface):
        """Dibuja el gráfico interactivo basado en los datos"""
        if not self.chart_data:
            return

        values = self.chart_data["values"]
        if not values:
            return

        # Calcular factores de escala
        max_val = max(values)
        min_val = min(values)
        val_range = max_val - min_val if max_val != min_val else 1

        # Ajustar para evitar división por cero
        val_range = max(val_range, 0.1)

        # Calcular dimensiones del área de dibujo (con márgenes)
        margin = 40
        graph_width = self.rect.width - 2 * margin
        graph_height = self.rect.height - 2 * margin
        graph_left = self.rect.left + margin
        graph_bottom = self.rect.bottom - margin

        # Dibujar título del gráfico
        title_text = f"{self.chart_data['tipo_dato']} - {self.chart_data['dispositivo']}"
        title_surface = self.font.render(title_text, True, (0, 0, 0))
        surface.blit(title_surface, (self.rect.left + margin, self.rect.top + 10))

        # Dibujar ejes
        pygame.draw.line(surface, (0, 0, 0),
                         (graph_left, graph_bottom),
                         (graph_left + graph_width, graph_bottom), 2)  # Eje X
        pygame.draw.line(surface, (0, 0, 0),
                         (graph_left, graph_bottom),
                         (graph_left, graph_bottom - graph_height), 2)  # Eje Y

        # Dibujar valores
        point_radius = 4
        hover_radius = 8
        points = []

        for i, value in enumerate(values):
            # Calcular posición X con desplazamiento y escala
            x_pos = graph_left + (i * graph_width / (len(values) - 1)) * self.scale_x + self.offset_x

            # Solo dibujar puntos visibles
            if graph_left <= x_pos <= graph_left + graph_width:
                y_pos = graph_bottom - ((value - min_val) / val_range) * graph_height
                points.append((x_pos, y_pos))

                # Dibujar punto
                color = (255, 0, 0) if self.hover_index == i else (0, 100, 255)
                radius = hover_radius if self.hover_index == i else point_radius
                pygame.draw.circle(surface, color, (int(x_pos), int(y_pos)), radius)

        # Dibujar líneas entre puntos
        if len(points) > 1:
            pygame.draw.lines(surface, (0, 100, 255), False, points, 2)

        # Dibujar estadísticas
        stats_text = [
            f"Último: {self.chart_data['stats']['last']:.1f}",
            f"Máx: {self.chart_data['stats']['max']:.1f}",
            f"Mín: {self.chart_data['stats']['min']:.1f}",
            f"Prom: {self.chart_data['stats']['avg']:.1f}"
        ]

        for i, text in enumerate(stats_text):
            text_surface = self.small_font.render(text, True, (0, 0, 0))
            surface.blit(text_surface, (self.rect.right - 100, self.rect.top + 20 + i * 20))

    def _draw_hover_info(self, surface: pygame.Surface):
        """Muestra información detallada al hacer hover sobre un punto"""
        if not self.chart_data or self.hover_index is None:
            return

        index = self.hover_index
        timestamp = self.chart_data["timestamps"][index]
        value = self.chart_data["values"][index]

        # Crear texto a mostrar
        info_text = [
            f"Fecha: {timestamp}",
            f"Valor: {value:.2f}"
        ]

        # Calcular posición del tooltip (evitar que salga de la pantalla)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_width = 200
        tooltip_height = 60

        if mouse_x + tooltip_width > surface.get_width():
            tooltip_x = surface.get_width() - tooltip_width - 10
        else:
            tooltip_x = mouse_x + 10

        if mouse_y + tooltip_height > surface.get_height():
            tooltip_y = mouse_y - tooltip_height - 10
        else:
            tooltip_y = mouse_y + 10

        # Dibujar tooltip
        pygame.draw.rect(surface, (255, 255, 220),
                         (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
        pygame.draw.rect(surface, (200, 200, 100),
                         (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 1)

        # Dibujar texto
        for i, text in enumerate(info_text):
            text_surface = self.small_font.render(text, True, (0, 0, 0))
            surface.blit(text_surface, (tooltip_x + 10, tooltip_y + 10 + i * 20))

    def handle_event(self, event: pygame.event.Event):
        """Maneja eventos de interacción con el gráfico"""
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover_index = None
            return

        if event.type == pygame.MOUSEMOTION:
            if self.chart_data:
                # Calcular índice del punto más cercano al mouse
                mouse_x, _ = event.pos
                margin = 40
                graph_left = self.rect.left + margin
                graph_width = self.rect.width - 2 * margin

                if graph_width > 0:
                    relative_x = (mouse_x - graph_left - self.offset_x) / (graph_width * self.scale_x)
                    index = int(relative_x * (len(self.chart_data["values"]) - 1))
                    index = max(0, min(index, len(self.chart_data["values"]) - 1))
                    self.hover_index = index

            if self.dragging:
                dx = event.pos[0] - self.last_mouse_x
                self.offset_x += dx
                max_offset = (self.rect.width - 80) * (self.scale_x - 1)
                self.offset_x = max(-max_offset, min(self.offset_x, 0))
                self.last_mouse_x = event.pos[0]

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                self.dragging = True
                self.last_mouse_x = event.pos[0]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Clic izquierdo
                self.dragging = False

        elif event.type == pygame.MOUSEWHEEL:
            if self.chart_data:
                # Zoom con la rueda del mouse
                zoom_factor = 1.1 if event.y > 0 else 0.9
                self.scale_x *= zoom_factor
                self.scale_x = max(1.0, min(self.scale_x, 5.0))  # Límites de zoom