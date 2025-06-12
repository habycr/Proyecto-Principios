
import sys
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.tarjeta import Tarjeta
from invernadero_inteligente.frontend.services.api_service import APIService
from components.usuarios.registro.elementos.input_box import InputBox
from components.usuarios.registro.elementos.password_box import PasswordBox
from invernadero_inteligente.frontend.services.api_service import APIService
import pygame
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton


class Configuracion:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_chica = pygame.font.Font(None, 18)
        self.ANCHO_MENU_SELECCION = 150  # Ancho del menú de selección

        # Opciones para los menús de selección
        self.opciones_tiempo = ["30s", "1 minuto", "2 minutos", "3 minutos", "5 minutos"]
        self.parametros = ["Temperatura", "Humedad de suelo", "Humedad ambiental", "Luz solar"]

        # Valores seleccionados (inicialmente 5 minutos)
        self.valores_seleccionados = {param: "5 minutos" for param in self.parametros}
        self.menu_abierto = None
        self.scroll_y = 0
        self.arrastrando_scroll = False

        self.crear_componentes()

    def crear_componentes(self):
        # Título principal
        self.titulo_principal = self.fuente_titulo.render("Configuración", True, (0, 0, 0))

        # Subtítulo de ajustes
        self.titulo_ajustes = self.fuente_normal.render("Ajuste de parámetros", True, (0, 0, 0))

        # Botón para parámetros por defecto
        self.boton_default = Boton(
            self.ancho // 2 - 100,
            self.alto - 120,
            300,
            40,
            "Parámetros por defecto",
            config.COLOR_BUTTON_SECONDARY
        )

        # Botón para volver al dashboard
        self.boton_volver = Boton(
            20,
            self.alto - 70,
            150,
            40,
            "Volver",
            config.COLOR_BUTTON_SECONDARY
        )

        # Rectángulos para los parámetros y botones de selección
        self.rects_parametros = {}
        self.rects_botones_seleccion = {}
        self.rects_menu_seleccion = None
        self.rects_opciones_menu = []
        self.rects_radios = []
        self.scroll_bar_rect = None

        # Espaciado vertical aumentado entre parámetros (120 píxeles)
        pos_y = 120
        for param in self.parametros:
            self.rects_parametros[param] = pygame.Rect(50, pos_y, 200, 30)
            self.rects_botones_seleccion[param] = pygame.Rect(260, pos_y, 150, 30)
            pos_y += 120

    def manejar_evento(self, evento):
        # Manejar eventos del menú de selección primero
        if self.menu_abierto:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clic izquierdo
                    mouse_pos = evento.pos

                    # Verificar clic en la barra de scroll
                    if self.scroll_bar_rect and self.scroll_bar_rect.collidepoint(mouse_pos):
                        self.arrastrando_scroll = True
                        return None

                    # Verificar clic en los radio buttons (sin clip)
                    for i, radio_rect in enumerate(self.rects_radios):
                        # Ajustar posición del rectángulo según el scroll
                        adjusted_radio_rect = pygame.Rect(
                            radio_rect.x,
                            radio_rect.y + self.scroll_y,
                            radio_rect.width,
                            radio_rect.height
                        )

                        if adjusted_radio_rect.collidepoint(mouse_pos):
                            nuevo_valor = self.opciones_tiempo[i]
                            if self.valores_seleccionados[self.menu_abierto] != nuevo_valor:
                                self.valores_seleccionados[self.menu_abierto] = nuevo_valor
                                print(f"Configuración actualizada - {self.menu_abierto}: {nuevo_valor}")
                            else:
                                print(f"El valor para {self.menu_abierto} se mantiene: {nuevo_valor}")
                            return None

                    # Cerrar menú si se hace clic fuera
                    if not self.rects_menu_seleccion.collidepoint(mouse_pos):
                        self.menu_abierto = None
                    return None

            elif evento.type == pygame.MOUSEBUTTONUP:
                if evento.button == 1:
                    self.arrastrando_scroll = False

            elif evento.type == pygame.MOUSEMOTION and self.arrastrando_scroll:
                # Manejar arrastre de la barra de scroll
                menu_top = self.rects_menu_seleccion.y
                relative_y = evento.pos[1] - menu_top
                total_height = len(self.opciones_tiempo) * 40
                visible_ratio = self.rects_menu_seleccion.height / total_height
                scroll_ratio = relative_y / self.rects_menu_seleccion.height
                self.scroll_y = -int((scroll_ratio - visible_ratio / 2) * total_height)

                # Limitar el scroll
                max_scroll = max(0, total_height - self.rects_menu_seleccion.height)
                self.scroll_y = max(-max_scroll, min(0, self.scroll_y))
                return None

            elif evento.type == pygame.MOUSEWHEEL:
                # Manejar scroll del mouse
                self.scroll_y += evento.y * 20
                total_height = len(self.opciones_tiempo) * 40
                max_scroll = max(0, total_height - self.rects_menu_seleccion.height)
                self.scroll_y = max(-max_scroll, min(0, self.scroll_y))
                return None

        # Resto de eventos solo si no hay menú abierto
        if self.menu_abierto is None and evento.type == pygame.MOUSEBUTTONDOWN:
            # Botón de parámetros por defecto
            if self.boton_default.rect.collidepoint(evento.pos):
                cambios = False
                for param in self.parametros:
                    if self.valores_seleccionados[param] != "5 minutos":
                        cambios = True
                    self.valores_seleccionados[param] = "5 minutos"

                if cambios:
                    print("Todos los parámetros han sido restablecidos a: 5 minutos")
                else:
                    print("Los parámetros ya estaban configurados con los valores por defecto (5 minutos)")
                return None

            # Botón volver
            elif self.boton_volver.rect.collidepoint(evento.pos):
                return "volver_dashboard"

            # Botones para abrir menú de selección
            for param in self.parametros:
                if self.rects_botones_seleccion[param].collidepoint(evento.pos):
                    self.menu_abierto = param
                    self.scroll_y = 0
                    print(f"Menú de selección abierto para {param}. Valor actual: {self.valores_seleccionados[param]}")
                    return None

        return None

    def dibujar(self, pantalla):
        pantalla.fill((255, 255, 255))

        # Dibujar título principal
        pantalla.blit(self.titulo_principal, (self.ancho // 2 - self.titulo_principal.get_width() // 2, 30))

        # Dibujar subtítulo de ajustes
        pantalla.blit(self.titulo_ajustes, (50, 80))

        # Dibujar parámetros y sus botones de selección
        for param in self.parametros:
            texto_param = self.fuente_normal.render(param, True, (0, 0, 0))
            pantalla.blit(texto_param, (self.rects_parametros[param].x, self.rects_parametros[param].y))

            pygame.draw.rect(pantalla, (200, 200, 200), self.rects_botones_seleccion[param])
            pygame.draw.rect(pantalla, (0, 0, 0), self.rects_botones_seleccion[param], 2)
            texto_valor = self.fuente_normal.render(self.valores_seleccionados[param], True, (0, 0, 0))
            pantalla.blit(texto_valor,
                          (self.rects_botones_seleccion[param].x + 10, self.rects_botones_seleccion[param].y + 5))

        # Dibujar menú de selección si hay uno abierto
        if self.menu_abierto:
            index_param = self.parametros.index(self.menu_abierto)
            pos_y_base = 120 + index_param * 120 + 40

            # Crear rectángulo del menú de selección (mostrar 3 opciones)
            menu_height = 120  # 3 opciones * 40px cada una
            self.rects_menu_seleccion = pygame.Rect(260, pos_y_base, self.ANCHO_MENU_SELECCION, menu_height)

            # Dibujar fondo del menú
            pygame.draw.rect(pantalla, (240, 240, 240), self.rects_menu_seleccion)
            pygame.draw.rect(pantalla, (0, 0, 0), self.rects_menu_seleccion, 2)

            # Configurar área de recorte solo para el dibujo
            old_clip = pantalla.get_clip()
            pantalla.set_clip(self.rects_menu_seleccion)

            # Dibujar opciones con radio buttons
            self.rects_opciones_menu = []
            self.rects_radios = []
            for i, opcion in enumerate(self.opciones_tiempo):
                opcion_y = pos_y_base + i * 40 + self.scroll_y
                opcion_rect = pygame.Rect(260, opcion_y, self.ANCHO_MENU_SELECCION, 40)
                self.rects_opciones_menu.append(opcion_rect)

                # Dibujar radio button (bolita)
                radio_rect = pygame.Rect(265, opcion_y + 12, 16, 16)
                self.rects_radios.append(pygame.Rect(265, opcion_y + 12, 16, 16))  # Guardar posición real

                # Resaltar la opción si el mouse está sobre ella
                mouse_pos = pygame.mouse.get_pos()
                if opcion_rect.collidepoint(mouse_pos[0], mouse_pos[1] - self.scroll_y):
                    pygame.draw.rect(pantalla, (220, 220, 220), opcion_rect)

                # Dibujar radio button (círculo exterior)
                pygame.draw.circle(pantalla, (0, 0, 0), (radio_rect.x + 8, radio_rect.y + 8), 8, 1)

                # Rellenar el radio button si está seleccionado
                if self.valores_seleccionados[self.menu_abierto] == opcion:
                    pygame.draw.circle(pantalla, (0, 100, 255), (radio_rect.x + 8, radio_rect.y + 8), 6)

                # Dibujar texto de la opción
                texto_opcion = self.fuente_chica.render(opcion, True, (0, 0, 0))
                pantalla.blit(texto_opcion, (radio_rect.x + 25, radio_rect.y - 4))

            pantalla.set_clip(old_clip)

            # Dibujar barra de scroll si es necesario
            if len(self.opciones_tiempo) * 40 > menu_height:
                total_height = len(self.opciones_tiempo) * 40
                visible_ratio = menu_height / total_height
                scroll_ratio = -self.scroll_y / total_height

                scroll_height = max(20, int(menu_height * visible_ratio))
                scroll_pos = int(scroll_ratio * (menu_height - scroll_height))

                # Dibujar track de la barra
                pygame.draw.rect(pantalla, (200, 200, 200),
                                 (260 + self.ANCHO_MENU_SELECCION - 12, pos_y_base, 10, menu_height))
                # Dibujar barra deslizante
                self.scroll_bar_rect = pygame.Rect(
                    260 + self.ANCHO_MENU_SELECCION - 12,
                    pos_y_base + scroll_pos,
                    10,
                    scroll_height
                )
                pygame.draw.rect(pantalla, (120, 120, 120), self.scroll_bar_rect)
                pygame.draw.rect(pantalla, (80, 80, 80), self.scroll_bar_rect, 1)

        # Dibujar botones (si no hay menú abierto)
        if self.menu_abierto is None:
            self.boton_default.dibujar(pantalla)
            self.boton_volver.dibujar(pantalla)