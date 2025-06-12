# frontend/components/dashboard/dashboard.py
import pygame
import sys

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

        # Mensaje inferior
        mensaje = pygame.font.Font(None, 24).render(
            "Esta es una vista básica del dashboard",
            True,
            (150, 150, 150)
        )
        superficie.blit(mensaje, (20, self.alto - 40))
