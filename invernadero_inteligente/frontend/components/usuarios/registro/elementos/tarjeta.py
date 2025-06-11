# frontend/components/elementos/tarjeta.py
import pygame


class Tarjeta:
    def __init__(self, x, y, ancho, alto, titulo):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.titulo = titulo
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_fondo = (255, 255, 255)
        self.color_borde = (200, 200, 200)
        self.fuente_titulo = pygame.font.Font(None, 28)

    def dibujar(self, superficie):
        # Fondo
        pygame.draw.rect(superficie, self.color_fondo, self.rect)
        pygame.draw.rect(superficie, self.color_borde, self.rect, 2)

        # Título
        texto = self.fuente_titulo.render(self.titulo, True, (0, 0, 0))
        superficie.blit(texto, (self.x + 10, self.y + 10))