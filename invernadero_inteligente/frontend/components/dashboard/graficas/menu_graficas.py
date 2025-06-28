# frontend/components/dashboard/graficas/menu_graficas.py

import pygame
from pygame.locals import USEREVENT
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.dropdown_v2 import PopupMenu
from invernadero_inteligente.frontend.components.dashboard.graficas.graph_maker import generar_grafica
from invernadero_inteligente.frontend.components.dashboard.graficas.calendario_selector import CalendarioSelector

from typing import Dict, Optional, Tuple


class MenuGraficas:
    def __init__(self, ancho_ventana: int, alto_ventana: int, usuario: Dict,
                 ancho_grafica=770, alto_grafica=520):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_mensajes = pygame.font.Font(None, 28)
        self.fuente_fechas = pygame.font.Font(None, 24)

        # Configuración del tamaño de la gráfica
        self.ancho_grafica = ancho_grafica
        self.alto_grafica = alto_grafica

        # Obtener dispositivos del usuario
        self.dispositivos = usuario.get('numero_serie', [])
        if not isinstance(self.dispositivos, list):
            self.dispositivos = [self.dispositivos] if self.dispositivos else []

        self.dispositivo_actual = self.dispositivos[0] if self.dispositivos else None

        # Dropdown de sensores
        self.menu_data = [
            "Temperatura",
            "Humedad",
            "Exposición a la luz",
            "Humedad del suelo",
            "Niveles de agua"
        ]
        self.popup_menu = PopupMenu(self.menu_data, x=20, y=130)
        self.tipo_dato_seleccionado = None
        self.imagen_grafica = None
        self.mensaje_error = None

        # Calendario selector
        self.calendario_selector = CalendarioSelector(ancho_ventana, alto_ventana)
        self.fecha_inicio_seleccionada: Optional[str] = None
        self.fecha_fin_seleccionada: Optional[str] = None

        # Crear componentes visuales
        self.crear_componentes()

    def crear_componentes(self):
        # Botón de dispositivo
        self.boton_dispositivo = Boton(
            x=self.ancho - 250,
            y=20,
            ancho=220,
            alto=40,
            texto=f"Dispositivo: {self.dispositivo_actual}" if self.dispositivo_actual else "Sin dispositivos",
            color=config.COLOR_BUTTON
        )

        # Botón para volver
        self.boton_volver = Boton(
            x=self.ancho - 170,
            y=self.alto - 70,
            ancho=150,
            alto=40,
            texto="Volver",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón que despliega el dropdown
        self.boton_menu = Boton(
            x=20,
            y=90,
            ancho=200,
            alto=40,
            texto="Seleccionar sensor",
            color=(200, 200, 200)
        )

        # Botón de refrescar
        self.boton_refrescar = Boton(
            x=240,
            y=90,
            ancho=120,
            alto=40,
            texto="Refrescar",
            color=(180, 220, 180)
        )

        # Botón de calendario
        self.boton_calendario = Boton(
            x=380,
            y=90,
            ancho=160,
            alto=40,
            texto="Seleccionar fechas",
            color=(255, 200, 100)
        )

        # Botón para limpiar fechas
        self.boton_limpiar_fechas = Boton(
            x=560,
            y=90,
            ancho=120,
            alto=40,
            texto="Limpiar fechas",
            color=(255, 150, 150)
        )

    def obtener_fechas_para_grafica(self) -> Tuple[Optional[str], Optional[str]]:
        """Retorna las fechas seleccionadas para usar en la generación de gráficas"""
        return self.fecha_inicio_seleccionada, self.fecha_fin_seleccionada

    def generar_grafica_con_fechas(self):
        """Genera la gráfica considerando las fechas seleccionadas"""
        if self.tipo_dato_seleccionado and self.dispositivo_actual:
            # Pasar las fechas al generador de gráficas si están disponibles
            fecha_inicio, fecha_fin = self.obtener_fechas_para_grafica()

            # Generar gráfica con filtros de fecha
            self.imagen_grafica = generar_grafica(
                self.tipo_dato_seleccionado,
                self.dispositivo_actual,
                ancho_px=self.ancho_grafica,
                alto_px=self.alto_grafica,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )

            # Mensaje informativo sobre el rango de fechas
            if fecha_inicio and fecha_fin:
                print(f"Generando gráfica desde {fecha_inicio} hasta {fecha_fin}")
            elif fecha_inicio:
                print(f"Generando gráfica desde {fecha_inicio}")
            elif fecha_fin:
                print(f"Generando gráfica hasta {fecha_fin}")
            else:
                print("Generando gráfica con todos los datos disponibles")

            self.mensaje_error = None
        else:
            self.mensaje_error = "Debes seleccionar un tipo de sensor antes de refrescar."

    def manejar_evento(self, evento):
        # Primero manejar eventos del calendario si está activo
        if self.calendario_selector.activo:
            resultado = self.calendario_selector.manejar_evento(evento)
            if resultado == "fechas_confirmadas":
                # Obtener las fechas seleccionadas
                self.fecha_inicio_seleccionada, self.fecha_fin_seleccionada = \
                    self.calendario_selector.obtener_fechas_seleccionadas()
                print(f"Fechas confirmadas: {self.fecha_inicio_seleccionada} - {self.fecha_fin_seleccionada}")
                return "redraw"
            elif resultado == "cancelado":
                return "redraw"
            return None

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_volver.rect.collidepoint(evento.pos):
                return "volver_dashboard"

            elif self.boton_dispositivo.rect.collidepoint(evento.pos) and len(self.dispositivos) > 1:
                current_idx = self.dispositivos.index(self.dispositivo_actual)
                next_idx = (current_idx + 1) % len(self.dispositivos)
                self.dispositivo_actual = self.dispositivos[next_idx]
                self.boton_dispositivo.texto = f"Dispositivo: {self.dispositivo_actual}"
                return "redraw"

            elif self.boton_menu.rect.collidepoint(evento.pos):
                self.popup_menu.toggle()

            elif self.boton_refrescar.rect.collidepoint(evento.pos):
                self.generar_grafica_con_fechas()

            elif self.boton_calendario.rect.collidepoint(evento.pos):
                self.calendario_selector.abrir()
                return "redraw"

            elif self.boton_limpiar_fechas.rect.collidepoint(evento.pos):
                self.fecha_inicio_seleccionada = None
                self.fecha_fin_seleccionada = None
                self.calendario_selector.fecha_inicio = None
                self.calendario_selector.fecha_fin = None
                print("Fechas limpiadas")
                return "redraw"

            # Dropdown selection
            seleccion = self.popup_menu.handle_event(evento)
            if seleccion:
                self.boton_menu.texto = seleccion
                self.tipo_dato_seleccionado = seleccion
                self.mensaje_error = None
                print(f"Sensor seleccionado: {seleccion}")

        if evento.type == USEREVENT and evento.code == 'MENU':
            print(f"Evento MENU recibido: {evento.name}.{evento.item_id} - {evento.text}")

        return None

    def dibujar_info_fechas(self, superficie):
        """Dibuja la información de las fechas seleccionadas"""
        y_pos = 145

        if self.fecha_inicio_seleccionada or self.fecha_fin_seleccionada:
            # Título de la sección de fechas
            titulo_fechas = self.fuente_fechas.render("Rango de fechas seleccionado:", True, (50, 50, 50))
            superficie.blit(titulo_fechas, (20, y_pos))
            y_pos += 25

            # Fecha de inicio
            if self.fecha_inicio_seleccionada:
                texto_inicio = f"Desde: {self.fecha_inicio_seleccionada}"
                fecha_inicio_surface = self.fuente_fechas.render(texto_inicio, True, (0, 120, 0))
                superficie.blit(fecha_inicio_surface, (30, y_pos))
            else:
                texto_inicio = "Desde: No seleccionada"
                fecha_inicio_surface = self.fuente_fechas.render(texto_inicio, True, (150, 150, 150))
                superficie.blit(fecha_inicio_surface, (30, y_pos))

            y_pos += 20

            # Fecha de fin
            if self.fecha_fin_seleccionada:
                texto_fin = f"Hasta: {self.fecha_fin_seleccionada}"
                fecha_fin_surface = self.fuente_fechas.render(texto_fin, True, (120, 0, 0))
                superficie.blit(fecha_fin_surface, (30, y_pos))
            else:
                texto_fin = "Hasta: No seleccionada"
                fecha_fin_surface = self.fuente_fechas.render(texto_fin, True, (150, 150, 150))
                superficie.blit(fecha_fin_surface, (30, y_pos))
        else:
            # Mensaje cuando no hay fechas seleccionadas
            mensaje_sin_fechas = self.fuente_fechas.render("Sin rango de fechas (se mostrarán todos los datos)", True,
                                                           (100, 100, 100))
            superficie.blit(mensaje_sin_fechas, (20, y_pos))

    def dibujar(self, superficie):
        superficie.fill(config.BACKGROUND_COLOR)

        # Título
        titulo = self.fuente_titulo.render("Información del Dispositivo", True, (0, 0, 0))
        superficie.blit(titulo, (20, 20))

        # Botones
        self.boton_dispositivo.dibujar(superficie)
        self.boton_volver.dibujar(superficie)
        self.boton_menu.dibujar(superficie)
        self.boton_refrescar.dibujar(superficie)
        self.boton_calendario.dibujar(superficie)
        self.boton_limpiar_fechas.dibujar(superficie)

        # Información de fechas seleccionadas
        self.dibujar_info_fechas(superficie)

        # Gráfica (se dibuja antes del dropdown y calendario para que queden detrás)
        if self.imagen_grafica:
            grafica_x = self.ancho // 2 - self.imagen_grafica.get_width() // 2
            grafica_y = 220  # Posición ajustada para dar espacio a la info de fechas
            superficie.blit(self.imagen_grafica, (grafica_x, grafica_y))

        # Dropdown (se dibuja después para que aparezca sobre la gráfica)
        self.popup_menu.draw(superficie)

        # Error si no se ha seleccionado tipo de dato
        if self.mensaje_error:
            msg_surface = self.fuente_mensajes.render(self.mensaje_error, True, (255, 0, 0))
            superficie.blit(msg_surface, (20, 200))

        if not self.dispositivos:
            mensaje = self.fuente_titulo.render("No hay dispositivos asociados", True, (255, 0, 0))
            superficie.blit(mensaje, (self.ancho // 2 - 150, self.alto // 2 - 50))

        # Calendario selector (se dibuja al final para que aparezca sobre todo)
        self.calendario_selector.dibujar(superficie)