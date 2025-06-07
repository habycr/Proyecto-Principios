# frontend/components/usuarios/registro/elementos/input_box.py
import pygame


class InputBox:
    def __init__(self, x, y, ancho, alto, texto_placeholder=""):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = pygame.Color('lightskyblue3')
        self.color_activo = pygame.Color('dodgerblue2')
        self.color_texto = pygame.Color('black')
        self.texto = ""
        self.texto_placeholder = texto_placeholder
        self.fuente = pygame.font.Font(None, 32)
        self.activo = False

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activo = self.rect.collidepoint(evento.pos)
            self.color = self.color_activo if self.activo else pygame.Color('lightskyblue3')

        if evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_RETURN:
                self.activo = False
                self.color = pygame.Color('lightskyblue3')
            elif evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            else:
                self.texto += evento.unicode

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect, 2)

        # Renderizar texto o placeholder
        if self.texto:
            texto_surface = self.fuente.render(self.texto, True, self.color_texto)
        else:
            texto_surface = self.fuente.render(self.texto_placeholder, True, pygame.Color('gray'))

        superficie.blit(texto_surface, (self.rect.x + 5, self.rect.y + 5))

        # Mostrar cursor si está activo
        if self.activo:
            pygame.draw.line(superficie, self.color_texto,
                             (self.rect.x + 5 + texto_surface.get_width(), self.rect.y + 5),
                             (self.rect.x + 5 + texto_surface.get_width(), self.rect.y + self.rect.height - 5))