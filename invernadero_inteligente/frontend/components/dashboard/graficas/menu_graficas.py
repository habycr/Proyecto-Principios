# frontend/components/dashboard/graficas/menu_graficas.py

import pygame
from pygame.locals import USEREVENT
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.dropdown_v2 import PopupMenu
from invernadero_inteligente.frontend.components.dashboard.graficas.graph_maker import generar_grafica

from typing import Dict


class MenuGraficas:
    def __init__(self, ancho_ventana: int, alto_ventana: int, usuario: Dict,
                 ancho_grafica=770, alto_grafica=520):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_mensajes = pygame.font.Font(None, 28)

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

    def manejar_evento(self, evento):
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
                if self.tipo_dato_seleccionado and self.dispositivo_actual:
                    self.imagen_grafica = generar_grafica(
                        self.tipo_dato_seleccionado,
                        self.dispositivo_actual,
                        ancho_px=self.ancho_grafica,
                        alto_px=self.alto_grafica
                    )
                    self.mensaje_error = None
                else:
                    self.mensaje_error = "Debes seleccionar un tipo de sensor antes de refrescar."

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

        # Gráfica (se dibuja antes del dropdown para que quede detrás)
        if self.imagen_grafica:
            grafica_x = self.ancho // 2 - self.imagen_grafica.get_width() // 2
            grafica_y = 180  # Posición ajustada para la gráfica más pequeña
            superficie.blit(self.imagen_grafica, (grafica_x, grafica_y))

        # Dropdown (se dibuja después para que aparezca sobre la gráfica)
        self.popup_menu.draw(superficie)

        # Error si no se ha seleccionado tipo de dato
        if self.mensaje_error:
            msg_surface = self.fuente_mensajes.render(self.mensaje_error, True, (255, 0, 0))
            superficie.blit(msg_surface, (20, 180))

        if not self.dispositivos:
            mensaje = self.fuente_titulo.render("No hay dispositivos asociados", True, (255, 0, 0))
            superficie.blit(mensaje, (self.ancho // 2 - 150, self.alto // 2 - 50))