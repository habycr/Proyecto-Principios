# frontend/components/dashboard/dashboard.py
import threading
import time
import pygame
import requests

from io import BytesIO
from pygame import gfxdraw
from components.dashboard.configuracion import Configuracion
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.tarjeta import Tarjeta
from invernadero_inteligente.frontend.services.api_service import APIService
from invernadero_inteligente.firmware import esp32cam_to_drive
from invernadero_inteligente.firmware.timelapse_viewer import TimelapseViewer
from invernadero_inteligente.frontend.components.dashboard.editar_perfil.editar_perfil import EditarPerfil
from invernadero_inteligente.frontend.components.dashboard.alertas.menu_alertas import MenuAlertas
# Importar los nuevos controladores
from invernadero_inteligente.firmware.controladores.esp32_controller import ESP32Controller
from invernadero_inteligente.firmware.controladores.device_manager import DeviceManager


class Dashboard:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 28)
        self.fuente_pequena = pygame.font.Font(None, 24)

        # Inicializar controladores ESP32
        self.esp32_controller = ESP32Controller("http://172.19.14.137")
        self.device_manager = DeviceManager(self.esp32_controller)

        # Cargar la imagen
        self.imagen = Dashboard.cargar_imagen_desde_github()

        # Variables para el temporizador de abono - MEJORADAS del Dashboard 2
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
        self.editando_perfil = False
        self.editar_perfil = None
        self.en_menu_alertas = False
        self.menu_alertas = None
        # Variables para captura automática
        self.autocapture = False
        self.capture_thread = None

        self.crear_componentes()

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

        # Botón para capturar imagen
        self.boton_capturar = Boton(
            x=300,
            y=150,
            ancho=200,
            alto=50,
            texto="Capturar Foto",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón para abrir timelapse
        self.boton_timelapse = Boton(
            x=300,
            y=220,
            ancho=200,
            alto=50,
            texto="Ver Timelapse",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón para ver gráficos
        self.boton_graficos = Boton(
            x=300,
            y=290,
            ancho=200,
            alto=50,
            texto="Gráficos",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Crear botones de dispositivos dinámicamente basados en device_manager
        self.botones_dispositivos = {}
        dispositivos_config = {
            "bomba_agua": {"x": 50, "y": 150, "ancho": 260},
            "ventilador": {"x": 50, "y": 220, "ancho": 200},
            "uv": {"x": 50, "y": 290, "ancho": 260},
            "techo": {"x": 50, "y": 360, "ancho": 200}
        }

        for dispositivo, config_pos in dispositivos_config.items():
            texto_inicial = self.device_manager.obtener_texto_boton(dispositivo)
            color_inicial = self.device_manager.obtener_color_boton(dispositivo)

            self.botones_dispositivos[dispositivo] = Boton(
                x=config_pos["x"],
                y=config_pos["y"],
                ancho=config_pos["ancho"],
                alto=50,
                texto=texto_inicial,
                color=color_inicial
            )

        # Botón para el temporizador de abono - IMPLEMENTACIÓN DEL DASHBOARD 2
        self.boton_abono = Boton(
            x=50,
            y=420,
            ancho=200,
            alto=50,
            texto="Configurar abono",
            color=(100, 200, 100)  # Verde claro
        )

        # Botón principal
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
            x=0,
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

        # Botón de editar perfil
        self.boton_editar_perfil = Boton(
            x=self.ancho - 170,
            y=140,
            ancho=150,
            alto=40,
            texto="Editar perfil",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón para soporte técnico
        self.boton_soporte = Boton(
            x=self.ancho - 170,
            y=200,
            ancho=150,
            alto=40,
            texto="Soporte técnico",
            color=config.COLOR_BUTTON_SECONDARY
        )

        # Botón para alertas
        self.boton_alertas = Boton(
            x=300,
            y=360,  # Posicionado después del botón de gráficos
            ancho=200,
            alto=50,
            texto="Alertas",
            color=config.COLOR_BUTTON_SECONDARY
        )

    def manejar_evento(self, evento):
        if self.editando_perfil:
            resultado = self.editar_perfil.manejar_evento(evento)
            if resultado == "volver_dashboard":
                self.editando_perfil = False
                return "redraw"
            elif resultado == "perfil_actualizado":
                self.editando_perfil = False
                self.usuario = self.editar_perfil.obtener_datos_actualizados()
                return "perfil_actualizado"
            return None

        if self.en_menu_alertas:
            resultado = self.menu_alertas.manejar_evento(evento)
            if resultado == "volver_dashboard":
                self.en_menu_alertas = False
                return "redraw"
            elif resultado == "redraw":
                return "redraw"
            return None

        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Manejar clic en la X de la ventana de alerta PRIMERO
            if self.mostrar_alerta:
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
                # Si clickean en el popup, no procesamos otros botones
                if popup_rect.collidepoint(evento.pos):
                    return None

            # Manejar clics en el diálogo de configuración de tiempo SEGUNDO
            if self.configurando_tiempo:
                # Verificar si el click está dentro del diálogo
                dialogo_rect = pygame.Rect(self.ancho // 2 - 200, self.alto // 2 - 150, 400, 300)
                if not dialogo_rect.collidepoint(evento.pos):
                    # Click fuera del diálogo, no hacer nada
                    return None

                if self.boton_aceptar_tiempo.rect.collidepoint(evento.pos):
                    self.tiempo_duracion_temporizador = (self.tiempo_horas * 3600 +
                                                         self.tiempo_minutos * 60 +
                                                         self.tiempo_segundos)
                    if self.tiempo_duracion_temporizador > 0:
                        self.temporizador_activo = True
                        self.tiempo_inicio_temporizador = time.time()
                        self.boton_abono.texto = "Cancelar abono"
                        self.boton_abono.color = (200, 100, 100)
                    self.configurando_tiempo = False
                    return "redraw"
                elif self.boton_cancelar_tiempo.rect.collidepoint(evento.pos):
                    self.configurando_tiempo = False
                    return "redraw"

                # Cambiar campo de entrada activa
                for i, campo in enumerate(["horas", "minutos", "segundos"]):
                    rect = pygame.Rect(self.ancho // 2 - 50, self.alto // 2 - 70 + i * 40, 100, 30)
                    if rect.collidepoint(evento.pos):
                        self.entrada_activa = campo
                        self.texto_entrada = str(getattr(self, f"tiempo_{campo}"))
                        return None
                return None

            # Botones principales del dashboard
            if self.boton_cerrar.rect.collidepoint(evento.pos):
                return "logout"
            elif self.boton_configuracion.rect.collidepoint(evento.pos):
                return "configuracion"
            elif self.boton_alertas.rect.collidepoint(evento.pos):
                self.en_menu_alertas = True
                self.menu_alertas = MenuAlertas(self.ancho, self.alto)
                return "redraw"
            elif self.boton_soporte.rect.collidepoint(evento.pos):
                return "soporte"
            elif self.boton_graficos.rect.collidepoint(evento.pos):
                return "graficos"
            elif self.boton_principal.rect.collidepoint(evento.pos):
                print("Botón principal presionado")
            elif self.boton_editar_perfil.rect.collidepoint(evento.pos):
                self.editando_perfil = True
                self.editar_perfil = EditarPerfil(self.ancho, self.alto, self.usuario)
                return "redraw"
            elif self.boton_capturar.rect.collidepoint(evento.pos):
                print("Capturando y subiendo imagen")
                esp32cam_to_drive.take_photo_and_upload()
                print("Imagen capturada con éxito")
            elif self.boton_timelapse.rect.collidepoint(evento.pos):
                print("Timelapse presionado")
                self.ver_timelapse()

            # IMPLEMENTACIÓN DEL BOTÓN DE ABONO DEL DASHBOARD 2
            elif self.boton_abono.rect.collidepoint(evento.pos):
                if self.temporizador_activo:
                    # Cancelar el temporizador
                    self.temporizador_activo = False
                    self.boton_abono.texto = "Configurar abono"
                    self.boton_abono.color = (100, 200, 100)
                    return "redraw"
                else:
                    # Abrir configuración de tiempo
                    self.configurando_tiempo = True
                    self.tiempo_horas = 0
                    self.tiempo_minutos = 0
                    self.tiempo_segundos = 0
                    self.texto_entrada = ""
                    self.entrada_activa = "horas"
                    return "redraw"

            # Manejar clics en los botones de dispositivos usando DeviceManager
            for dispositivo, boton in self.botones_dispositivos.items():
                if boton.rect.collidepoint(evento.pos):
                    resultado = self.device_manager.controlar_dispositivo(dispositivo)

                    if resultado["exito"]:
                        # Actualizar el botón con los nuevos valores
                        boton.texto = resultado["nuevo_texto"]
                        boton.color = resultado["nuevo_color"]
                        print(resultado["mensaje"])
                    else:
                        print(f"Error: {resultado['mensaje']}")

                    return None

        # Manejar entrada de texto para configurar el tiempo - MEJORADO DEL DASHBOARD 2
        elif evento.type == pygame.KEYDOWN and self.configurando_tiempo:
            if evento.key == pygame.K_RETURN:
                self.tiempo_duracion_temporizador = (self.tiempo_horas * 3600 +
                                                     self.tiempo_minutos * 60 +
                                                     self.tiempo_segundos)
                if self.tiempo_duracion_temporizador > 0:
                    self.temporizador_activo = True
                    self.tiempo_inicio_temporizador = time.time()
                    self.boton_abono.texto = "Cancelar abono"
                    self.boton_abono.color = (200, 100, 100)
                self.configurando_tiempo = False
                return "redraw"
            elif evento.key == pygame.K_ESCAPE:
                self.configurando_tiempo = False
                return "redraw"
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
            return "redraw"

        return None

    def actualizar(self):
        # Verificar si el temporizador ha terminado - MEJORADO DEL DASHBOARD 2
        if self.temporizador_activo:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_temporizador
            tiempo_restante = self.tiempo_duracion_temporizador - tiempo_transcurrido

            if tiempo_restante <= 0:
                # El temporizador ha terminado
                self.temporizador_activo = False
                self.mostrar_alerta = True
                self.alerta_tiempo = time.time()
                self.boton_abono.texto = "Configurar abono"
                self.boton_abono.color = (100, 200, 100)
                print("¡Temporizador de abono terminado! Mostrando alerta.")
                return "redraw"

        # Cerrar alerta automáticamente después de 10 segundos - DEL DASHBOARD 2
        if self.mostrar_alerta and time.time() - self.alerta_tiempo > 10:
            self.mostrar_alerta = False
            return "redraw"

        return None

    def dibujar_popup_abono(self, superficie):
        """Dibuja el pop-up de abono centrado en la pantalla - MEJORADO DEL DASHBOARD 2"""
        ancho_popup = 400
        alto_popup = 200

        # Posición centrada
        x = (self.ancho - ancho_popup) // 2
        y = (self.alto - alto_popup) // 2

        # Fondo semitransparente oscuro
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        superficie.blit(overlay, (0, 0))

        # Fondo del pop-up con sombra
        sombra_rect = pygame.Rect(x + 5, y + 5, ancho_popup, alto_popup)
        pygame.draw.rect(superficie, (0, 0, 0, 100), sombra_rect)

        # Fondo principal del pop-up
        pygame.draw.rect(superficie, (255, 255, 255), (x, y, ancho_popup, alto_popup))
        pygame.draw.rect(superficie, (255, 0, 0), (x, y, ancho_popup, alto_popup), 3)

        # Dibujar botón X para cerrar
        close_rect = pygame.Rect(x + ancho_popup - 30, y + 10, 20, 20)
        pygame.draw.rect(superficie, (255, 200, 200), close_rect)
        pygame.draw.line(superficie, (255, 0, 0), (close_rect.left + 3, close_rect.top + 3),
                         (close_rect.right - 3, close_rect.bottom - 3), 3)
        pygame.draw.line(superficie, (255, 0, 0), (close_rect.left + 3, close_rect.bottom - 3),
                         (close_rect.right - 3, close_rect.top + 3), 3)

        # Título del pop-up
        titulo = self.fuente_titulo.render("¡APLICAR ABONO!", True, (255, 0, 0))
        superficie.blit(titulo, (x + (ancho_popup - titulo.get_width()) // 2, y + 30))

        # Mensaje
        mensaje = self.fuente_normal.render("Es hora de aplicar abono", True, (0, 0, 0))
        superficie.blit(mensaje, (x + (ancho_popup - mensaje.get_width()) // 2, y + 80))

        mensaje2 = self.fuente_normal.render("a tus plantas.", True, (0, 0, 0))
        superficie.blit(mensaje2, (x + (ancho_popup - mensaje2.get_width()) // 2, y + 120))

        # Instrucción para cerrar
        instruccion = self.fuente_pequena.render("Haz clic en la X para cerrar", True, (100, 100, 100))
        superficie.blit(instruccion, (x + (ancho_popup - instruccion.get_width()) // 2, y + 160))

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
        # Si estamos editando perfil, solo mostrar esa vista
        if self.editando_perfil:
            self.editar_perfil.dibujar(superficie)
            return

        if self.en_menu_alertas:
            self.menu_alertas.dibujar(superficie)
            return

        # Fondo claro
        superficie.fill(config.BACKGROUND_COLOR)

        # Título principal
        titulo = self.fuente_titulo.render(f"Bienvenido, {self.usuario['nombre']}", True, (0, 0, 0))
        superficie.blit(titulo, (20, 20))

        # Información del usuario
        dispositivos = ", ".join(self.usuario.get('numero_serie', [])) if isinstance(self.usuario.get('numero_serie'),
                                                                                     list) else self.usuario.get(
            'numero_serie', 'N/A')
        info_usuario = self.fuente_normal.render(
            f"Rol: {self.usuario['rol']} | Dispositivo: {dispositivos}",
            True,
            (100, 100, 100)
        )
        superficie.blit(info_usuario, (20, 70))

        # Dibujar botones
        self.boton_cerrar.dibujar(superficie)
        self.boton_configuracion.dibujar(superficie)
        self.boton_capturar.dibujar(superficie)
        self.boton_timelapse.dibujar(superficie)
        self.boton_graficos.dibujar(superficie)
        self.boton_alertas.dibujar(superficie)

        # Dibujar botones de dispositivos
        for boton in self.botones_dispositivos.values():
            boton.dibujar(superficie)

        # Dibujar botón de abono
        self.boton_abono.dibujar(superficie)

        # Dibujar botones inferiores
        self.boton_principal.dibujar(superficie)
        self.boton_editar_perfil.dibujar(superficie)
        self.boton_soporte.dibujar(superficie)

        # MOSTRAR TIEMPO RESTANTE DEL TEMPORIZADOR - MEJORADO DEL DASHBOARD 2
        if self.temporizador_activo:
            tiempo_transcurrido = time.time() - self.tiempo_inicio_temporizador
            tiempo_restante = max(0, self.tiempo_duracion_temporizador - tiempo_transcurrido)

            horas = min(99, int(tiempo_restante // 3600))
            minutos = min(59, int((tiempo_restante % 3600) // 60))
            segundos = min(59, int(tiempo_restante % 60))

            # Fondo para el contador
            contador_rect = pygame.Rect(50, 485, 300, 40)
            pygame.draw.rect(superficie, (255, 255, 200), contador_rect)
            pygame.draw.rect(superficie, (200, 200, 0), contador_rect, 2)

            texto_tiempo = self.fuente_normal.render(
                f"Próximo abono en: {horas:02d}:{minutos:02d}:{segundos:02d}",
                True, (0, 0, 0))
            superficie.blit(texto_tiempo, (55, 495))

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

                # Texto
                texto_valor = self.texto_entrada if self.entrada_activa == campo else str(valor)
                texto_render = self.fuente_normal.render(texto_valor, True, (0, 0, 0))
                superficie.blit(texto_render, (self.ancho // 2 - 45, self.alto // 2 - 65 + i * 40))

            # Botones Aceptar y Cancelar
            self.boton_aceptar_tiempo.x = self.ancho // 2 - 130
            self.boton_aceptar_tiempo.y = self.alto // 2 + 80
            # Crear o actualizar el rect del botón
            if not hasattr(self.boton_aceptar_tiempo, 'rect') or self.boton_aceptar_tiempo.rect is None:
                self.boton_aceptar_tiempo.rect = pygame.Rect(
                    self.boton_aceptar_tiempo.x,
                    self.boton_aceptar_tiempo.y,
                    120, 40
                )
            else:
                self.boton_aceptar_tiempo.rect.x = self.boton_aceptar_tiempo.x
                self.boton_aceptar_tiempo.rect.y = self.boton_aceptar_tiempo.y
            self.boton_aceptar_tiempo.dibujar(superficie)

            self.boton_cancelar_tiempo.x = self.ancho // 2 + 10
            self.boton_cancelar_tiempo.y = self.alto // 2 + 80
            # Crear o actualizar el rect del botón
            if not hasattr(self.boton_cancelar_tiempo, 'rect') or self.boton_cancelar_tiempo.rect is None:
                self.boton_cancelar_tiempo.rect = pygame.Rect(
                    self.boton_cancelar_tiempo.x,
                    self.boton_cancelar_tiempo.y,
                    120, 40
                )
            else:
                self.boton_cancelar_tiempo.rect.x = self.boton_cancelar_tiempo.x
                self.boton_cancelar_tiempo.rect.y = self.boton_cancelar_tiempo.y
            self.boton_cancelar_tiempo.dibujar(superficie)

        # DIBUJAR POP-UP DE ABONO (DEBE SER LO ÚLTIMO PARA ESTAR ENCIMA)
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
            pos_x = 480
            pos_y = 20
            superficie.blit(imagen_pequena, (pos_x, pos_y))

    def iniciar_captura(self, intervalo=300):
        if not self.autocapture:
            self.autocapture = True
            self.capture_thread = threading.Thread(target=self._captura_loop, args=(intervalo,), daemon=True)
            self.capture_thread.start()
            print("Captura automática iniciada")
        else:
            print("Ya se está capturando la imagen")

    def _captura_loop(self, intervalo):
        while self.autocapture:
            try:
                print("Capturando imagen")
                esp32cam_to_drive.take_photo_and_upload()
            except Exception as e:
                print(f"Error en la captura: {e}")
            time.sleep(intervalo)

    def ver_timelapse(self):
        viewer = TimelapseViewer(
            screen=pygame.display.get_surface(),
            folder_id="1bJyt5g4C0I054B8viTvOzSLac1ksq0Wc",
        )
        viewer.descargar_imagenes()
        viewer.mostrar_timelapse(duracion=0.5)

    def obtener_estado_dispositivo(self, dispositivo: str) -> bool:
        """Método de compatibilidad - delega al device_manager"""
        return self.device_manager.obtener_estado_dispositivo(dispositivo)

    def resetear_todos_dispositivos(self):
        """Resetea todos los dispositivos usando el device_manager"""
        self.device_manager.resetear_todos_dispositivos()
        # Actualizar la UI de los botones
        for dispositivo, boton in self.botones_dispositivos.items():
            boton.texto = self.device_manager.obtener_texto_boton(dispositivo)
            boton.color = self.device_manager.obtener_color_boton(dispositivo)