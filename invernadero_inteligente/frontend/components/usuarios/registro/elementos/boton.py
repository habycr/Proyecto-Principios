# frontend/components/usuarios/registro/elementos/boton.py
import pygame


class Boton:
    def __init__(self, x, y, ancho, alto, texto, color):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.texto = texto
        self.fuente = pygame.font.Font(None, 32)

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, self.rect)
        pygame.draw.rect(superficie, (0, 0, 0), self.rect, 2)

        texto_surface = self.fuente.render(self.texto, True, (0, 0, 0))
        superficie.blit(texto_surface,
                        (self.rect.x + (self.rect.width - texto_surface.get_width()) // 2,
                         self.rect.y + (self.rect.height - texto_surface.get_height()) // 2))