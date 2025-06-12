# frontend/components/dashboard/dashboard.py
import pygame
import sys
import requests

from components.dashboard.configuracion import Configuracion
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.tarjeta import Tarjeta  # Asumiré que creas este componente
from invernadero_inteligente.frontend.services.api_service import APIService


class Dashboard:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 28)
        # URL base del ESP32 - AJUSTA ESTO CON TU IP REAL
        self.esp32_base_url = "http://192.168.0.26"
        # Estados de los dispositivos (False = apagado, True = encendido)
        self.estados_dispositivos = {
            "bomba_agua": False,
            "ventilador": False,
            "uv": False,
            "techo": False
        }
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
                ancho=200,
                alto=50,
                texto="Activar Bomba de Agua",
                color=config.COLOR_BUTTON  # Verde por defecto (apagado)
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
                ancho=200,
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
        # Botón principal de ejemplo
        self.boton_principal = Boton(
            x=self.ancho // 2 - 100,
            y=self.alto // 2,
            ancho=200,
            alto=50,
            texto="Mi Dispositivo",
            color=config.COLOR_BUTTON
        )

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_cerrar.rect.collidepoint(evento.pos):
                return "logout"
            elif self.boton_configuracion.rect.collidepoint(evento.pos):
                return "configuracion"

            elif self.boton_principal.rect.collidepoint(evento.pos):
                print("Botón principal presionado")  # Acción de ejemplo

            # Manejar clics en los botones de dispositivos
            for dispositivo, boton in self.botones_dispositivos.items():
                if boton.rect.collidepoint(evento.pos):
                    # Determinar la acción basada en el estado actual
                    if dispositivo == "techo":
                        accion = "adelante" if not self.estados_dispositivos[dispositivo] else "stop"
                        endpoint = "motorA"  # Asumimos que el techo usa motorA

                    elif dispositivo == "bomba_agua":  # Mapeo especial para bomba
                        accion = "encender" if not self.estados_dispositivos[dispositivo] else "apagar"
                        endpoint = "bomba"  # Usamos "bomba" que es el endpoint en el ESP32

                    else:
                        accion = "encender" if not self.estados_dispositivos[dispositivo] else "apagar"
                        endpoint = dispositivo

                    # Enviar comando al ESP32
                    if self.enviar_comando(endpoint, accion):
                        # Cambiar el estado solo si el comando fue exitoso
                        self.estados_dispositivos[dispositivo] = not self.estados_dispositivos[dispositivo]

                        # Actualizar el botón según el nuevo estado
                        if self.estados_dispositivos[dispositivo]:
                            boton.color = (255, 0, 0)  # Rojo
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
        self.boton_principal.dibujar(superficie)
        self.boton_configuracion.dibujar(superficie)
        # Dibujar botones de dispositivos
        for boton in self.botones_dispositivos.values():
            boton.dibujar(superficie)
        # Mensaje inferior
        mensaje = pygame.font.Font(None, 24).render(
            "Esta es una vista básica del dashboard",
            True,
            (150, 150, 150)
        )
        superficie.blit(mensaje, (20, self.alto - 40))
