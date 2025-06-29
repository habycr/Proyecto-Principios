# frontend/components/dashboard/dashboard_admin.py
import pygame
from invernadero_inteligente.frontend.config import config
from components.usuarios.registro.elementos.boton import Boton
from components.usuarios.registro.registro_usuario import RegistroUsuario
from components.usuarios.gestion_tickets_admin.gestion_tickets_admin import GestionTicketsAdmin


class DashboardAdmin:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 28)

        # Estados de las ventanas
        self.mostrar_registro = False
        self.mostrar_gestion_tickets = False

        # Instancias de las ventanas
        self.registro_usuario = RegistroUsuario(ancho_ventana, alto_ventana)
        self.gestion_tickets = GestionTicketsAdmin(ancho_ventana, alto_ventana)

        # Botones
        self.boton_cerrar = Boton(
            x=ancho_ventana - 170, y=20,
            ancho=150, alto=40,
            texto="Cerrar sesión",
            color=config.COLOR_BUTTON_SECONDARY
        )
        self.boton_registrar = Boton(
            x=ancho_ventana // 2 - 100, y=200,
            ancho=200, alto=50,
            texto="Registrar Usuario",
            color=config.COLOR_BUTTON
        )
        self.boton_gestionar_tickets = Boton(
            x=ancho_ventana // 2 - 100, y=300,
            ancho=200, alto=50,
            texto="Gestionar Tickets",
            color=config.COLOR_BUTTON
        )

    def manejar_evento(self, evento):
        # Manejar eventos de la ventana de registro
        if self.mostrar_registro:
            resultado = self.registro_usuario.manejar_evento(evento)
            if resultado == "volver":
                self.mostrar_registro = False
            return

        # Manejar eventos de la ventana de gestión de tickets
        if self.mostrar_gestion_tickets:
            resultado = self.gestion_tickets.manejar_evento(evento)
            if resultado == "volver":
                self.mostrar_gestion_tickets = False
            return

        # Manejar eventos del dashboard principal
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_cerrar.rect.collidepoint(evento.pos):
                return "logout"
            elif self.boton_registrar.rect.collidepoint(evento.pos):
                self.mostrar_registro = True
            elif self.boton_gestionar_tickets.rect.collidepoint(evento.pos):
                self.mostrar_gestion_tickets = True

    def dibujar(self, superficie):
        superficie.fill(config.BACKGROUND_COLOR)

        # Mostrar ventana de registro si está activa
        if self.mostrar_registro:
            self.registro_usuario.dibujar(superficie)
            return

        # Mostrar ventana de gestión de tickets si está activa
        if self.mostrar_gestion_tickets:
            self.gestion_tickets.dibujar(superficie)
            return

        # Dibujar dashboard principal
        titulo = self.fuente_titulo.render(f"Panel de Administrador", True, (0, 0, 0))
        superficie.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 50))

        nombre = self.usuario.get("nombre", "Admin")
        info = self.fuente_normal.render(f"Bienvenido, {nombre}", True, (80, 80, 80))
        superficie.blit(info, (self.ancho // 2 - info.get_width() // 2, 100))

        # Dibujar botones
        self.boton_cerrar.dibujar(superficie)
        self.boton_registrar.dibujar(superficie)
        self.boton_gestionar_tickets.dibujar(superficie)
