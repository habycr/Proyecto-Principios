# frontend/components/dashboard/graficas/calendario_selector.py

import pygame
import calendar
from datetime import datetime, date
from typing import Optional, Tuple
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton


class CalendarioSelector:
    def __init__(self, ancho_ventana: int, alto_ventana: int):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.activo = False

        # Configuración visual
        self.fuente_titulo = pygame.font.Font(None, 24)
        self.fuente_texto = pygame.font.Font(None, 20)
        self.fuente_pequena = pygame.font.Font(None, 18)

        # Estado del calendario
        self.anio_actual = datetime.now().year
        self.mes_actual = datetime.now().month
        self.fecha_inicio: Optional[date] = None
        self.fecha_fin: Optional[date] = None
        self.seleccionando_inicio = True  # True para inicio, False para fin

        # Colores
        self.color_fondo = (250, 250, 250)
        self.color_header = (70, 130, 180)
        self.color_dia_normal = (220, 220, 220)
        self.color_dia_hover = (200, 200, 255)
        self.color_dia_seleccionado = (100, 150, 255)
        self.color_fecha_inicio = (50, 255, 50)
        self.color_fecha_fin = (255, 50, 50)
        self.color_rango = (200, 255, 200)

        # Dimensiones del calendario
        self.cal_ancho = 400
        self.cal_alto = 300
        self.cal_x = (ancho_ventana - self.cal_ancho) // 2
        self.cal_y = (alto_ventana - self.cal_alto - 200) // 2

        # Tamaño de celda del calendario
        self.celda_ancho = self.cal_ancho // 7
        self.celda_alto = 35

        self.crear_botones()

    def crear_botones(self):
        # Botones de navegación del calendario
        self.boton_anio_anterior = Boton(
            x=self.cal_x - 100,
            y=self.cal_y - 40,
            ancho=40,
            alto=30,
            texto="<<",
            color=(150, 150, 150)
        )

        self.boton_mes_anterior = Boton(
            x=self.cal_x - 50,
            y=self.cal_y - 40,
            ancho=40,
            alto=30,
            texto="<",
            color=(150, 150, 150)
        )

        self.boton_mes_siguiente = Boton(
            x=self.cal_x + self.cal_ancho + 10,
            y=self.cal_y - 40,
            ancho=40,
            alto=30,
            texto=">",
            color=(150, 150, 150)
        )

        self.boton_anio_siguiente = Boton(
            x=self.cal_x + self.cal_ancho + 60,
            y=self.cal_y - 40,
            ancho=40,
            alto=30,
            texto=">>",
            color=(150, 150, 150)
        )

        # Botones de acción
        self.boton_limpiar = Boton(
            x=self.cal_x,
            y=self.cal_y + self.cal_alto + 20,
            ancho=100,
            alto=35,
            texto="Limpiar",
            color=(255, 180, 180)
        )

        self.boton_confirmar = Boton(
            x=self.cal_x + 120,
            y=self.cal_y + self.cal_alto + 20,
            ancho=100,
            alto=35,
            texto="Confirmar",
            color=(180, 255, 180)
        )

        self.boton_cancelar = Boton(
            x=self.cal_x + 240,
            y=self.cal_y + self.cal_alto + 20,
            ancho=100,
            alto=35,
            texto="Cancelar",
            color=(220, 220, 220)
        )

        # Botones para alternar entre fecha inicio/fin
        self.boton_fecha_inicio = Boton(
            x=self.cal_x,
            y=self.cal_y - 80,
            ancho=150,
            alto=30,
            texto="Fecha Inicio",
            color=(180, 255, 180)
        )

        self.boton_fecha_fin = Boton(
            x=self.cal_x + 170,
            y=self.cal_y - 80,
            ancho=150,
            alto=30,
            texto="Fecha Fin",
            color=(255, 180, 180)
        )

    def abrir(self):
        """Abre la ventana de selección de fechas"""
        self.activo = True
        self.anio_actual = datetime.now().year
        self.mes_actual = datetime.now().month

    def cerrar(self):
        """Cierra la ventana de selección de fechas"""
        self.activo = False

    def obtener_fechas_seleccionadas(self) -> Tuple[Optional[str], Optional[str]]:
        """Retorna las fechas seleccionadas en formato string"""
        fecha_inicio_str = self.fecha_inicio.strftime("%d/%m/%Y") if self.fecha_inicio else None
        fecha_fin_str = self.fecha_fin.strftime("%d/%m/%Y") if self.fecha_fin else None
        return fecha_inicio_str, fecha_fin_str

    def manejar_evento(self, evento):
        if not self.activo:
            return None

        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Navegación de calendario
            if self.boton_anio_anterior.rect.collidepoint(evento.pos):
                if self.anio_actual > 2015:
                    self.anio_actual -= 1

            elif self.boton_mes_anterior.rect.collidepoint(evento.pos):
                self.mes_actual -= 1
                if self.mes_actual < 1:
                    self.mes_actual = 12
                    if self.anio_actual > 2015:
                        self.anio_actual -= 1

            elif self.boton_mes_siguiente.rect.collidepoint(evento.pos):
                self.mes_actual += 1
                if self.mes_actual > 12:
                    self.mes_actual = 1
                    if self.anio_actual < 2025:
                        self.anio_actual += 1

            elif self.boton_anio_siguiente.rect.collidepoint(evento.pos):
                if self.anio_actual < 2025:
                    self.anio_actual += 1

            # Selección de tipo de fecha
            elif self.boton_fecha_inicio.rect.collidepoint(evento.pos):
                self.seleccionando_inicio = True

            elif self.boton_fecha_fin.rect.collidepoint(evento.pos):
                self.seleccionando_inicio = False

            # Acciones
            elif self.boton_limpiar.rect.collidepoint(evento.pos):
                self.fecha_inicio = None
                self.fecha_fin = None

            elif self.boton_confirmar.rect.collidepoint(evento.pos):
                if self.fecha_inicio and self.fecha_fin:
                    self.cerrar()
                    return "fechas_confirmadas"

            elif self.boton_cancelar.rect.collidepoint(evento.pos):
                self.cerrar()
                return "cancelado"

            # Selección de día en el calendario
            else:
                dia_seleccionado = self._obtener_dia_clickeado(evento.pos)
                if dia_seleccionado:
                    nueva_fecha = date(self.anio_actual, self.mes_actual, dia_seleccionado)

                    if self.seleccionando_inicio:
                        self.fecha_inicio = nueva_fecha
                        # Auto-cambiar a seleccionar fecha fin
                        self.seleccionando_inicio = False
                    else:
                        self.fecha_fin = nueva_fecha

                    # Asegurar que fecha_inicio <= fecha_fin
                    if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
                        self.fecha_inicio, self.fecha_fin = self.fecha_fin, self.fecha_inicio

        return None

    def _obtener_dia_clickeado(self, pos_mouse) -> Optional[int]:
        """Determina qué día fue clickeado en el calendario"""
        mouse_x, mouse_y = pos_mouse

        # Verificar si el click está dentro del área del calendario
        if (self.cal_x <= mouse_x <= self.cal_x + self.cal_ancho and
                self.cal_y + 30 <= mouse_y <= self.cal_y + self.cal_alto):

            # Calcular fila y columna
            col = (mouse_x - self.cal_x) // self.celda_ancho
            fila = (mouse_y - (self.cal_y + 30)) // self.celda_alto

            if 0 <= col < 7 and 0 <= fila < 6:
                # Obtener el calendario del mes
                cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
                if fila < len(cal) and col < len(cal[fila]):
                    dia = cal[fila][col]
                    return dia if dia != 0 else None

        return None

    def dibujar(self, superficie):
        if not self.activo:
            return

        # Fondo semi-transparente
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        superficie.blit(overlay, (0, 0))

        # Fondo del calendario
        pygame.draw.rect(superficie, self.color_fondo,
                         (self.cal_x - 20, self.cal_y - 100,
                          self.cal_ancho + 40, self.cal_alto + 180))
        pygame.draw.rect(superficie, (0, 0, 0),
                         (self.cal_x - 20, self.cal_y - 100,
                          self.cal_ancho + 40, self.cal_alto + 180), 2)

        # Título del mes y año
        titulo = f"{calendar.month_name[self.mes_actual]} {self.anio_actual}"
        texto_titulo = self.fuente_titulo.render(titulo, True, (0, 0, 0))
        titulo_x = self.cal_x + (self.cal_ancho - texto_titulo.get_width()) // 2
        superficie.blit(texto_titulo, (titulo_x, self.cal_y - 40))

        # Información de fechas seleccionadas
        info_y = self.cal_y - 120
        if self.fecha_inicio:
            inicio_texto = f"Inicio: {self.fecha_inicio.strftime('%d/%m/%Y')}"
            texto_inicio = self.fuente_texto.render(inicio_texto, True, (0, 150, 0))
            superficie.blit(texto_inicio, (self.cal_x, info_y))

        if self.fecha_fin:
            fin_texto = f"Fin: {self.fecha_fin.strftime('%d/%m/%Y')}"
            texto_fin = self.fuente_texto.render(fin_texto, True, (150, 0, 0))
            superficie.blit(texto_fin, (self.cal_x + 200, info_y))

        # Indicador de qué fecha se está seleccionando
        modo_texto = "Seleccionando: " + ("Fecha Inicio" if self.seleccionando_inicio else "Fecha Fin")
        texto_modo = self.fuente_pequena.render(modo_texto, True, (100, 100, 100))
        superficie.blit(texto_modo, (self.cal_x, info_y + 20))

        # Días de la semana
        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, dia in enumerate(dias_semana):
            texto_dia = self.fuente_pequena.render(dia, True, (0, 0, 0))
            x = self.cal_x + i * self.celda_ancho + (self.celda_ancho - texto_dia.get_width()) // 2
            superficie.blit(texto_dia, (x, self.cal_y + 5))

        # Calendario
        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        for fila, semana in enumerate(cal):
            for col, dia in enumerate(semana):
                if dia == 0:
                    continue

                x = self.cal_x + col * self.celda_ancho
                y = self.cal_y + 30 + fila * self.celda_alto

                # Determinar color de fondo
                fecha_actual = date(self.anio_actual, self.mes_actual, dia)
                color_fondo = self.color_dia_normal

                if self.fecha_inicio and self.fecha_fin:
                    if self.fecha_inicio <= fecha_actual <= self.fecha_fin:
                        color_fondo = self.color_rango

                if fecha_actual == self.fecha_inicio:
                    color_fondo = self.color_fecha_inicio
                elif fecha_actual == self.fecha_fin:
                    color_fondo = self.color_fecha_fin

                # Dibujar celda
                pygame.draw.rect(superficie, color_fondo,
                                 (x, y, self.celda_ancho, self.celda_alto))
                pygame.draw.rect(superficie, (100, 100, 100),
                                 (x, y, self.celda_ancho, self.celda_alto), 1)

                # Dibujar número del día
                texto_dia = self.fuente_texto.render(str(dia), True, (0, 0, 0))
                texto_x = x + (self.celda_ancho - texto_dia.get_width()) // 2
                texto_y = y + (self.celda_alto - texto_dia.get_height()) // 2
                superficie.blit(texto_dia, (texto_x, texto_y))

        # Dibujar botones
        self.boton_anio_anterior.dibujar(superficie)
        self.boton_mes_anterior.dibujar(superficie)
        self.boton_mes_siguiente.dibujar(superficie)
        self.boton_anio_siguiente.dibujar(superficie)
        self.boton_fecha_inicio.dibujar(superficie)
        self.boton_fecha_fin.dibujar(superficie)
        self.boton_limpiar.dibujar(superficie)
        self.boton_confirmar.dibujar(superficie)
        self.boton_cancelar.dibujar(superficie)

        # Actualizar colores de botones según el estado
        if self.seleccionando_inicio:
            self.boton_fecha_inicio.color = (100, 255, 100)
            self.boton_fecha_fin.color = (255, 180, 180)
        else:
            self.boton_fecha_inicio.color = (180, 255, 180)
            self.boton_fecha_fin.color = (255, 100, 100)