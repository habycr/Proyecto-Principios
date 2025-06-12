# frontend/components/dashboard/dashboard.py
import pygame
import sys
import requests
import time
from io import BytesIO
from pygame import gfxdraw
from components.dashboard.configuracion import Configuracion
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.tarjeta import Tarjeta
from invernadero_inteligente.frontend.services.api_service import APIService


class Dashboard:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 28)
        self.fuente_pequena = pygame.font.Font(None, 24)
        # URL base del ESP32 - AJUSTA ESTO CON TU IP REAL
        self.esp32_base_url = "http://192.168.0.26"
        # Cargar la imagen
        self.imagen = Dashboard.cargar_imagen_desde_github()
        # Estados de los dispositivos (False = apagado, True = encendido)
        self.estados_dispositivos = {
            "bomba_agua": False,
            "ventilador": False,
            "uv": False,
            "techo": False
        }

        # Variables para el temporizador de abono
        self.temporizador_activo = False
        self.tiempo_inicio_temporizador = 0
        self.tiempo_duracion_temporizador = 0  # en segundos
        self.mostrar_alerta = False
        self.alerta_tiempo = 0
        self.configurando_tiempo = False
        self.tiempo_horas = 0
        self.tiempo_minutos = 0
        self.tiempo_segundos = 0
        self.texto_entrada = ""
        self.entrada_activa = "horas"

        self.crear_componentes()

    def enviar_comando(self, dispositivo, accion):
        try:
            url = f"{self.esp32_base_url}/{dispositivo}/{accion}"
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Comando {accion} para {dispositivo} enviado correctamente")
                return True
            else:
                print(f"Error al enviar comando: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error de conexión: {str(e)}")
            return False

    def crear_componentes(self):
        # Botón de cerrar sesión
        self.boton_cerrar = Boton(
            x=self.ancho - 170,
            y=20,
            ancho=150,
            alto=40,
            texto="Cerrar sesión",
            color=config.COLOR_BUTTON_SECONDARY
        )
        # Botón de configuración
        self.boton_configuracion = Boton(
            x=self.ancho - 170,
            y=80,
            ancho=150,
            alto=40,
            texto="Configuración",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botones de control de dispositivos
        self.botones_dispositivos = {
            "bomba_agua": Boton(
                x=50,
                y=150,
                ancho=260,
                alto=50,
                texto="Activar Bomba de Agua",
                color=config.COLOR_BUTTON
            ),
            "ventilador": Boton(
                x=50,
                y=220,
                ancho=200,
                alto=50,
                texto="Activar Ventilador",
                color=config.COLOR_BUTTON
            ),
            "uv": Boton(
                x=50,
                y=290,
                ancho=260,
                alto=50,
                texto="Activar Luz Ultravioleta",
                color=config.COLOR_BUTTON
            ),
            "techo": Boton(
                x=50,
                y=360,
                ancho=200,
                alto=50,
                texto="Abrir Techo",
                color=config.COLOR_BUTTON
            )
        }

        # Botón para el temporizador de abono
        self.boton_abono = Boton(
            x=50,
            y=420,
            ancho=260,
            alto=50,
            texto="Próximo aviso de abono",
            color=(100, 200, 100)  # Verde claro
        )

        # Botón para configurar el tiempo (ahora al lado del botón de abono)
        self.boton_config_tiempo = Boton(
            x=340,
            y=420,
            ancho=190,
            alto=50,
            texto="Configurar tiempo",
            color=(200, 200, 100)
        )

        # Botón principal movido hacia abajo
        self.boton_principal = Boton(
            x=self.ancho // 2 - 100,
            y=550,
            ancho=200,
            alto=50,
            texto="Mi Dispositivo",
            color=config.COLOR_BUTTON
        )

        # Botones para el diálogo de configuración de tiempo
        self.boton_aceptar_tiempo = Boton(
            x=0,  # Posiciones se ajustarán al dibujar
            y=0,
            ancho=120,
            alto=40,
            texto="Aceptar",
            color=(100, 200, 100)
        )

        self.boton_cancelar_tiempo = Boton(
            x=0,
            y=0,
            ancho=120,
            alto=40,
            texto="Cancelar",
            color=(200, 100, 100)
        )

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_cerrar.rect.collidepoint(evento.pos):
                return "logout"
            elif self.boton_configuracion.rect.collidepoint(evento.pos):
                return "configuracion"
            elif self.boton_principal.rect.collidepoint(evento.pos):
                print("Botón principal presionado")

            # Manejar clics en los botones de dispositivos
            for dispositivo, boton in self.botones_dispositivos.items():
                if boton.rect.collidepoint(evento.pos):
                    if dispositivo == "techo":
                        accion = "adelante" if not self.estados_dispositivos[dispositivo] else "stop"
                        endpoint = "motorA"
                    elif dispositivo == "bomba_agua":
                        accion = "encender" if not self.estados_dispositivos[dispositivo] else "apagar"
                        endpoint = "bomba"
                    else:
                        accion = "encender" if not self.estados_dispositivos[dispositivo] else "apagar"
                        endpoint = dispositivo

                    if self.enviar_comando(endpoint, accion):
                        self.estados_dispositivos[dispositivo] = not self.estados_dispositivos[dispositivo]
                        if self.estados_dispositivos[dispositivo]:
                            boton.color = (255, 0, 0)
                            if dispositivo == "techo":
                                boton.texto = "Cerrar Techo"
                            elif dispositivo == "bomba_agua":
                                boton.texto = "Desactivar Bomba Agua"
                            else:
                                boton.texto = boton.texto.replace("Activar", "Desactivar")
                        else:
                            boton.color = config.COLOR_BUTTON
                            if dispositivo == "techo":
                                boton.texto = "Abrir Techo"
                            elif dispositivo == "bomba_agua":
                                boton.texto = "Activar Bomba Agua"
                            else:
                                boton.texto = boton.texto.replace("Desactivar", "Activar")
                    return None

            # Manejar clic en el botón de abono (solo para cancelar)
            if self.boton_abono.rect.collidepoint(evento.pos) and self.temporizador_activo:
                self.temporizador_activo = False
                self.boton_abono.color = (100, 200, 100)
                self.boton_abono.texto = "Próximo aviso de abono"

            # Manejar clic en el botón de configurar tiempo
            elif self.boton_config_tiempo.rect.collidepoint(evento.pos) and not self.configurando_tiempo:
                self.configurando_tiempo = True
                self.tiempo_horas = 0
                self.tiempo_minutos = 0
                self.tiempo_segundos = 0
                self.texto_entrada = ""
                self.entrada_activa = "horas"

            # Manejar clics en el diálogo de configuración de tiempo
            if self.configurando_tiempo:
                # Botón Aceptar
                if self.boton_aceptar_tiempo.rect.collidepoint(evento.pos):
                    self.tiempo_duracion_temporizador = (self.tiempo_horas * 3600 +
                                                         self.tiempo_minutos * 60 +
                                                         self.tiempo_segundos)
                    if self.tiempo_duracion_temporizador > 0:
                        self.temporizador_activo = True
                        self.tiempo_inicio_temporizador = time.time()
                        self.boton_abono.color = (200, 100, 100)
                        self.boton_abono.texto = "Cancelar aviso de abono"
                    self.configurando_tiempo = False

                # Botón Cancelar
                elif self.boton_cancelar_tiempo.rect.collidepoint(evento.pos):
                    self.configurando_tiempo = False

                # Cambiar campo de entrada activa
                for i, campo in enumerate(["horas", "minutos", "segundos"]):
                    rect = pygame.Rect(self.ancho // 2 - 50, self.alto // 2 - 50 + i * 40, 100, 30)
                    if rect.collidepoint(evento.pos):
                        self.entrada_activa = campo
                        self.texto_entrada = str(getattr(self, f"tiempo_{campo}"))

            # Manejar clic en la X de la ventana de alerta
            if self.mostrar_alerta:
                # Definir el área de la X (esquina superior derecha del popup)
                popup_rect = pygame.Rect(
                    (self.ancho - 400) // 2,
                    (self.alto - 200) // 2,
                    400,
                    200
                )
                close_rect = pygame.Rect(
                    popup_rect.right - 30,
                    popup_rect.top + 10,
                    20,
                    20
                )

                if close_rect.collidepoint(evento.pos):
                    self.mostrar_alerta = False
                    return "redraw"

        # Manejar entrada de texto para configurar el tiempo
        if self.configurando_tiempo and evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.tiempo_duracion_temporizador = (self.tiempo_horas * 3600 +
                                                     self.tiempo_minutos * 60 +
                                                     self.tiempo_segundos)
                if self.tiempo_duracion_temporizador > 0:
                    self.temporizador_activo = True
                    self.tiempo_inicio_temporizador = time.time()
                    self.boton_abono.color = (200, 100, 100)
                    self.boton_abono.texto = "Cancelar aviso de abono"
                self.configurando_tiempo = False

            elif evento.key == pygame.K_ESCAPE:
                self.configurando_tiempo = False

            elif evento.key == pygame.K_BACKSPACE:
                self.texto_entrada = self.texto_entrada[:-1]

            elif evento.unicode.isdigit():
                self.texto_entrada += evento.unicode

            # Actualizar el valor correspondiente
            if self.entrada_activa and self.texto_entrada:
                try:
                    valor = int(self.texto_entrada)
                    if self.entrada_activa == "horas" and 0 <= valor <= 100:
                        self.tiempo_horas = valor
                    elif self.entrada_activa == "minutos" and 0 <= valor < 60:
                        self.tiempo_minutos = valor
                    elif self.entrada_activa == "segundos" and 0 <= valor < 60:
                        self.tiempo_segundos = valor
                except ValueError:
                    pass

        return None

    def actualizar(self):
        # Verificar si el temporizador ha terminado
        if self.temporizador_activo:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_temporizador
            tiempo_restante = self.tiempo_duracion_temporizador - tiempo_transcurrido

            if tiempo_restante <= 0:  # Temporizador ha terminado
                self.temporizador_activo = False
                self.mostrar_alerta = True
                self.alerta_tiempo = time.time()
                self.boton_abono.color = (100, 200, 100)
                self.boton_abono.texto = "Próximo aviso de abono"
                return "redraw"

        return None

    def dibujar_popup_abono(self, superficie):
        """Dibuja el pop-up de abono centrado en la pantalla"""
        # Dimensiones del pop-up
        ancho_popup = 400
        alto_popup = 200

        # Posición centrada
        x = (self.ancho - ancho_popup) // 2
        y = (self.alto - alto_popup) // 2

        # Fondo semitransparente oscuro
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        superficie.blit(overlay, (0, 0))

        # Fondo del pop-up
        pygame.draw.rect(superficie, (255, 255, 255), (x, y, ancho_popup, alto_popup))
        pygame.draw.rect(superficie, (255, 0, 0), (x, y, ancho_popup, alto_popup), 3)

        # Dibujar botón X para cerrar (esquina superior derecha)
        close_rect = pygame.Rect(x + ancho_popup - 30, y + 10, 20, 20)
        pygame.draw.line(superficie, (255, 0, 0), (close_rect.left, close_rect.top),
                         (close_rect.right, close_rect.bottom), 2)
        pygame.draw.line(superficie, (255, 0, 0), (close_rect.left, close_rect.bottom),
                         (close_rect.right, close_rect.top), 2)

        # Título del pop-up
        titulo = self.fuente_titulo.render("¡ABONAR PLANTAS!", True, (255, 0, 0))
        superficie.blit(titulo, (x + (ancho_popup - titulo.get_width()) // 2, y + 30))

        # Mensaje
        mensaje = self.fuente_normal.render("El temporizador ha finalizado.", True, (0, 0, 0))
        superficie.blit(mensaje, (x + (ancho_popup - mensaje.get_width()) // 2, y + 80))

        mensaje2 = self.fuente_normal.render("Por favor, abone sus plantas.", True, (0, 0, 0))
        superficie.blit(mensaje2, (x + (ancho_popup - mensaje2.get_width()) // 2, y + 120))

    @staticmethod
    def cargar_imagen_desde_github():
        url = "https://raw.githubusercontent.com/habycr/Proyecto-Principios/6b91ab4a49c35c8810bff80b7b1b537ab67ffff6/invernadero_inteligente/frontend/components/usuarios/registro/elementos/logo/logo.png"
        try:
            response = requests.get(url)
            response.raise_for_status()
            imagen = pygame.image.load(BytesIO(response.content))
            return imagen
        except Exception as e:
            print(f"Error al cargar imagen desde GitHub: {e}")
            return None

    def dibujar(self, superficie):
        # Fondo claro
        superficie.fill(config.BACKGROUND_COLOR)

        # Título principal
        titulo = self.fuente_titulo.render(f"Bienvenido, {self.usuario['nombre']}", True, (0, 0, 0))
        superficie.blit(titulo, (20, 20))

        # Información del usuario
        info_usuario = self.fuente_normal.render(
            f"Rol: {self.usuario['rol']} | Dispositivo: {self.usuario.get('numero_serie', 'N/A')}",
            True,
            (100, 100, 100)
        )
        superficie.blit(info_usuario, (20, 70))

        # Dibujar botones
        self.boton_cerrar.dibujar(superficie)
        self.boton_configuracion.dibujar(superficie)

        # Dibujar botones de dispositivos
        for boton in self.botones_dispositivos.values():
            boton.dibujar(superficie)

        # Dibujar botones inferiores (alineados)
        self.boton_principal.dibujar(superficie)
        self.boton_abono.dibujar(superficie)
        self.boton_config_tiempo.dibujar(superficie)

        # Mostrar tiempo restante si el temporizador está activo
        if self.temporizador_activo:
            # Asegurarnos que tiempo_duracion_temporizador es un número válido
            if not hasattr(self, 'tiempo_duracion_temporizador') or not isinstance(self.tiempo_duracion_temporizador,
                                                                                   (int, float)):
                self.tiempo_duracion_temporizador = 0

            tiempo_transcurrido = time.time() - self.tiempo_inicio_temporizador
            tiempo_restante = max(0, self.tiempo_duracion_temporizador - tiempo_transcurrido)

            # Cálculo seguro de horas, minutos y segundos
            horas = min(99, int(tiempo_restante // 3600))  # Limitamos a 99 horas máximo
            minutos = min(59, int((tiempo_restante % 3600) // 60))
            segundos = min(59, int(tiempo_restante % 60))

            texto_tiempo = self.fuente_normal.render(
                f"Tiempo restante: {horas:02d}:{minutos:02d}:{segundos:02d}",
                True, (0, 0, 0))

            # Posición segura para el texto
            pos_y = min(510, self.alto - 30)
            superficie.blit(texto_tiempo, (320, pos_y))

        # Mostrar cuadro de configuración de tiempo
        if self.configurando_tiempo:
            # Fondo semitransparente
            s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            superficie.blit(s, (0, 0))

            # Cuadro de diálogo
            dialogo_rect = pygame.Rect(self.ancho // 2 - 200, self.alto // 2 - 150, 400, 300)
            pygame.draw.rect(superficie, (240, 240, 240), dialogo_rect)
            pygame.draw.rect(superficie, (0, 0, 0), dialogo_rect, 2)

            # Título
            titulo = self.fuente_titulo.render("Configurar aviso de abono", True, (0, 0, 0))
            superficie.blit(titulo, (self.ancho // 2 - 180, self.alto // 2 - 130))

            # Campos de entrada
            campos = [
                ("Horas (0-100):", "horas", self.tiempo_horas),
                ("Minutos (0-59):", "minutos", self.tiempo_minutos),
                ("Segundos (0-59):", "segundos", self.tiempo_segundos)
            ]

            for i, (etiqueta, campo, valor) in enumerate(campos):
                # Etiqueta
                texto = self.fuente_normal.render(etiqueta, True, (0, 0, 0))
                superficie.blit(texto, (self.ancho // 2 - 180, self.alto // 2 - 70 + i * 40))

                # Campo de entrada
                rect = pygame.Rect(self.ancho // 2 - 50, self.alto // 2 - 70 + i * 40, 100, 30)
                pygame.draw.rect(superficie, (255, 255, 255), rect)
                pygame.draw.rect(superficie, (0, 0, 255) if self.entrada_activa == campo else (0, 0, 0), rect, 2)

                # Texto (lo que el usuario está escribiendo o el valor actual)
                texto_valor = self.texto_entrada if self.entrada_activa == campo else str(valor)
                texto_render = self.fuente_normal.render(texto_valor, True, (0, 0, 0))
                superficie.blit(texto_render, (self.ancho // 2 - 45, self.alto // 2 - 65 + i * 40))

            # Botones Aceptar y Cancelar
            self.boton_aceptar_tiempo.x = self.ancho // 2 - 130
            self.boton_aceptar_tiempo.y = self.alto // 2 + 80
            self.boton_aceptar_tiempo.dibujar(superficie)

            self.boton_cancelar_tiempo.x = self.ancho // 2 + 10
            self.boton_cancelar_tiempo.y = self.alto // 2 + 80
            self.boton_cancelar_tiempo.dibujar(superficie)

        # Mostrar alerta de abono (DEBE SER LO ÚLTIMO QUE SE DIBUJA)
        if self.mostrar_alerta:
            self.dibujar_popup_abono(superficie)

        # Mensaje inferior
        mensaje = pygame.font.Font(None, 24).render(
            "Esta es una vista básica del dashboard",
            True,
            (150, 150, 150)
        )
        superficie.blit(mensaje, (20, self.alto - 40))

        # Dibujar imagen
        if self.imagen:
            imagen_pequena = pygame.transform.scale(self.imagen, (140, 90))
            superficie.blit(imagen_pequena, (480, 20))