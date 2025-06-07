import pygame
from elementos.input_box import InputBox
from elementos.boton import Boton


class RegistroDispositivo:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        self.color_active = pygame.Color('dodgerblue2')
        self.color_inactive = pygame.Color('lightskyblue3')

        # Campos del formulario
        self.numero_serie = InputBox(100, 100, 200, 32, "Número de serie")
        self.usuario = InputBox(100, 150, 200, 32, "Usuario asociado")
        self.ubicacion = InputBox(100, 200, 200, 32, "Ubicación")
        self.boton_registrar = Boton(100, 250, "Registrar", self._registrar)

        self.elementos = [self.numero_serie, self.usuario, self.ubicacion, self.boton_registrar]

    def _registrar(self):
        """Envía los datos al backend (RF02)"""
        if not self.numero_serie.text:
            print("Error: Número de serie es obligatorio")
            return

        print(f"Dispositivo registrado: {self.numero_serie.text}, Usuario: {self.usuario.text}")
        # Aquí iría la llamada al backend (RF34)

    def draw(self):
        """Renderiza todos los elementos"""
        self.screen.fill((240, 240, 240))
        for elemento in self.elementos:
            elemento.draw(self.screen)
        pygame.display.flip()

    def handle_event(self, event):
        """Gestiona eventos (clics, teclado)"""
        for elemento in self.elementos:
            elemento.handle_event(event)