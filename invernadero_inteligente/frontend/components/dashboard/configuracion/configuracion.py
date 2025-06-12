
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
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.usuario = usuario  # Guardar referencia al usuario actual
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_chica = pygame.font.Font(None, 18)
        self.ANCHO_MENU_SELECCION = 180

        # Opciones para los menús de selección
        self.opciones_tiempo = ["30s", "1 minuto", "2 minutos", "3 minutos", "5 minutos"]
        self.parametros = ["Temperatura", "Humedad de suelo", "Humedad ambiental", "Luz solar"]

        # Valores seleccionados
        self.valores_seleccionados = {param: "5 minutos" for param in self.parametros}
        self.menu_abierto = None
        self.rects_radios = []

        # Variables para el campo de dispositivo
        self.texto_dispositivo = ""
        self.activo_campo_texto = False
        self.rect_campo_texto = pygame.Rect(50, self.alto - 180, 200, 40)
        self.boton_confirmar = Boton(
            260,
            self.alto - 180,
            150,
            40,
            "Confirmar",
            config.COLOR_BUTTON_SECONDARY
        )
        self.mostrar_aviso = False
        self.tiempo_aviso = 0
        self.mensaje_aviso = ""
        self.color_aviso = (0, 0, 0)  # Negro por defecto

        self.crear_componentes()

    def crear_componentes(self):
        # Título principal
        self.titulo_principal = self.fuente_titulo.render("Configuración", True, (0, 0, 0))

        # Subtítulo de ajustes
        self.titulo_ajustes = self.fuente_normal.render("Ajuste de parámetros", True, (0, 0, 0))

        # Título de Número de Dispositivo
        self.titulo_numerodeserie = self.fuente_normal.render("Para añadir dispositivos: ", True, (0, 0, 0))

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

                    # Verificar clic en los radio buttons
                    for i, radio_rect in enumerate(self.rects_radios):
                        if radio_rect.collidepoint(mouse_pos):
                            nuevo_valor = self.opciones_tiempo[i]
                            self.valores_seleccionados[self.menu_abierto] = nuevo_valor
                            self.menu_abierto = None
                            return None

                    # Verificar clic en las opciones del menú
                    for i, opcion in enumerate(self.opciones_tiempo):
                        opcion_rect = pygame.Rect(
                            self.rects_menu_seleccion.x,
                            self.rects_menu_seleccion.y + i * 40,
                            self.rects_menu_seleccion.width,
                            40
                        )
                        if opcion_rect.collidepoint(mouse_pos):
                            nuevo_valor = self.opciones_tiempo[i]
                            self.valores_seleccionados[self.menu_abierto] = nuevo_valor
                            self.menu_abierto = None
                            return None

                    # Cerrar menú si se hace clic fuera
                    if not self.rects_menu_seleccion.collidepoint(mouse_pos):
                        self.menu_abierto = None
                    return None

        # Manejar eventos del campo de texto
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Clic izquierdo
                mouse_pos = evento.pos

                # Activar/desactivar campo de texto
                if self.rect_campo_texto.collidepoint(mouse_pos):
                    self.activo_campo_texto = True
                else:
                    self.activo_campo_texto = False

                # Manejar botón de confirmar
                if self.boton_confirmar.rect.collidepoint(mouse_pos) and self.texto_dispositivo:
                    try:
                        # Obtener el email del usuario actual (deberías tener esto almacenado)
                        user_email = self.usuario["email"]


                        # Llamar al servicio para agregar el dispositivo
                        response = APIService.agregar_dispositivo(user_email, self.texto_dispositivo)

                        if response.get("status") == "success":
                            self.mensaje_aviso = "Dispositivo agregado exitosamente!"
                            self.color_aviso = (0, 150, 0)  # Verde para éxito
                        else:
                            self.mensaje_aviso = response.get("message", "Error al agregar dispositivo")
                            self.color_aviso = (150, 0, 0)  # Rojo para error

                        self.mostrar_aviso = True
                        self.tiempo_aviso = pygame.time.get_ticks()
                        self.texto_dispositivo = ""  # Limpiar el campo después de agregar
                    except Exception as e:
                        self.mensaje_aviso = f"Error: {str(e)}"
                        self.color_aviso = (150, 0, 0)
                        self.mostrar_aviso = True
                        self.tiempo_aviso = pygame.time.get_ticks()
                    return None

        # Manejar entrada de texto
        if self.activo_campo_texto and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if self.texto_dispositivo:
                    try:
                        user_email = self.usuario["email"]
                        response = APIService.agregar_dispositivo(user_email, self.texto_dispositivo)

                        if response.get("status") == "success":
                            self.mensaje_aviso = "Dispositivo agregado exitosamente!"
                            self.color_aviso = (0, 150, 0)
                        else:
                            self.mensaje_aviso = response.get("message", "Error al agregar dispositivo")
                            self.color_aviso = (150, 0, 0)

                        self.mostrar_aviso = True
                        self.tiempo_aviso = pygame.time.get_ticks()
                        self.texto_dispositivo = ""
                    except Exception as e:
                        self.mensaje_aviso = f"Error: {str(e)}"
                        self.color_aviso = (150, 0, 0)
                        self.mostrar_aviso = True
                        self.tiempo_aviso = pygame.time.get_ticks()
            elif evento.key == pygame.K_BACKSPACE:
                self.texto_dispositivo = self.texto_dispositivo[:-1]
            else:
                if len(self.texto_dispositivo) < 20 and evento.unicode.isalnum():
                    self.texto_dispositivo += evento.unicode

        # Resto de eventos solo si no hay menú abierto
        if self.menu_abierto is None and evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_default.rect.collidepoint(evento.pos):
                cambios = False
                for param in self.parametros:
                    if self.valores_seleccionados[param] != "5 minutos":
                        cambios = True
                    self.valores_seleccionados[param] = "5 minutos"

                if cambios:
                    print("Todos los parámetros han sido restablecidos a: 5 minutos")
                return None

            elif self.boton_volver.rect.collidepoint(evento.pos):
                return "volver_dashboard"

            for param in self.parametros:
                if self.rects_botones_seleccion[param].collidepoint(evento.pos):
                    self.menu_abierto = param
                    return None

        return None

    def dibujar(self, pantalla):
        pantalla.fill((255, 255, 255))

        # Dibujar título principal
        pantalla.blit(self.titulo_principal, (self.ancho // 2 - self.titulo_principal.get_width() // 2, 30))

        # Dibujar subtítulo de ajustes
        pantalla.blit(self.titulo_ajustes, (50, 80))

        # Dibujar subtítulo de número de dispositivo
        pantalla.blit(self.titulo_numerodeserie, (50, 600))

        # Dibujar parámetros y sus botones de selección
        for param in self.parametros:
            texto_param = self.fuente_normal.render(param, True, (0, 0, 0))
            pantalla.blit(texto_param, (self.rects_parametros[param].x, self.rects_parametros[param].y))

            pygame.draw.rect(pantalla, (200, 200, 200), self.rects_botones_seleccion[param])
            pygame.draw.rect(pantalla, (0, 0, 0), self.rects_botones_seleccion[param], 2)
            texto_valor = self.fuente_normal.render(self.valores_seleccionados[param], True, (0, 0, 0))
            pantalla.blit(texto_valor,
                          (self.rects_botones_seleccion[param].x + 10, self.rects_botones_seleccion[param].y + 5))

        # Dibujar campo de texto para dispositivo
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect_campo_texto)
        pygame.draw.rect(pantalla, (0, 0, 0) if self.activo_campo_texto else (100, 100, 100), self.rect_campo_texto, 2)

        # Dibujar texto ingresado o placeholder
        if self.texto_dispositivo or self.activo_campo_texto:
            texto_surface = self.fuente_normal.render(self.texto_dispositivo, True, (0, 0, 0))
            pantalla.blit(texto_surface, (self.rect_campo_texto.x + 10, self.rect_campo_texto.y + 10))
        else:
            texto_placeholder = self.fuente_normal.render("Número de serie", True, (150, 150, 150))
            pantalla.blit(texto_placeholder, (self.rect_campo_texto.x + 10, self.rect_campo_texto.y + 10))

        # Dibujar botón de confirmar
        self.boton_confirmar.dibujar(pantalla)

        # Dibujar botones
        self.boton_default.dibujar(pantalla)
        self.boton_volver.dibujar(pantalla)

        # Dibujar aviso si es necesario
        if self.mostrar_aviso:
            if pygame.time.get_ticks() - self.tiempo_aviso < 2000:  # Mostrar por 2 segundos
                aviso = self.fuente_normal.render(self.mensaje_aviso, True, self.color_aviso)
                pantalla.blit(aviso, (self.ancho // 2 - aviso.get_width() // 2, self.alto - 220))
            else:
                self.mostrar_aviso = False

        # Dibujar menú de selección si hay uno abierto
        if self.menu_abierto:
            index_param = self.parametros.index(self.menu_abierto)
            pos_y_base = 120 + index_param * 120 + 40

            menu_height = len(self.opciones_tiempo) * 40
            if pos_y_base + menu_height > self.alto - 100:
                pos_y_base = self.alto - 100 - menu_height

            self.rects_menu_seleccion = pygame.Rect(
                260,
                pos_y_base,
                self.ANCHO_MENU_SELECCION,
                menu_height
            )

            pygame.draw.rect(pantalla, (220, 220, 220), self.rects_menu_seleccion.inflate(5, 5))
            pygame.draw.rect(pantalla, (240, 240, 240), self.rects_menu_seleccion)
            pygame.draw.rect(pantalla, (0, 0, 0), self.rects_menu_seleccion, 2)

            self.rects_radios = []
            for i, opcion in enumerate(self.opciones_tiempo):
                opcion_y = pos_y_base + i * 40
                opcion_rect = pygame.Rect(260, opcion_y, self.ANCHO_MENU_SELECCION, 40)

                mouse_pos = pygame.mouse.get_pos()
                if opcion_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(pantalla, (220, 220, 220), opcion_rect)

                radio_rect = pygame.Rect(265, opcion_y + 12, 16, 16)
                self.rects_radios.append(radio_rect)

                pygame.draw.circle(pantalla, (0, 0, 0), (radio_rect.x + 8, radio_rect.y + 8), 8, 1)

                if self.valores_seleccionados[self.menu_abierto] == opcion:
                    pygame.draw.circle(pantalla, (0, 100, 255), (radio_rect.x + 8, radio_rect.y + 8), 6)

                texto_opcion = self.fuente_chica.render(opcion, True, (0, 0, 0))
                pantalla.blit(texto_opcion, (radio_rect.x + 25, radio_rect.y - 4))