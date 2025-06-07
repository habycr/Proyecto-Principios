# frontend/components/dispositivos/registro/elementos/dropdown.py
import pygame


class Dropdown:
    def __init__(self, x, y, ancho, alto, opciones):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = pygame.Color('lightskyblue3')
        self.opciones = opciones
        self.seleccion_actual = opciones[0]
        self.desplegado = False
        self.fuente = pygame.font.Font(None, 32)

        # Crear rects para las opciones
        self.opcion_rects = []
        for i in range(len(opciones)):
            self.opcion_rects.append(pygame.Rect(x, y + (i + 1) * alto, ancho, alto))

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos):
                self.desplegado = not self.desplegado
            elif self.desplegado:
                for i, rect in enumerate(self.opcion_rects):
                    if rect.collidepoint(evento.pos) and i < len(self.opciones):
                        self.seleccion_actual = self.opciones[i]
                        self.desplegado = False
                        break

    def dibujar(self, superficie):
        # Dibujar el cuadro principal
        pygame.draw.rect(superficie, self.color, self.rect)
        pygame.draw.rect(superficie, (0, 0, 0), self.rect, 2)

        # Dibujar texto seleccionado
        texto_surface = self.fuente.render(self.seleccion_actual, True, (0, 0, 0))
        superficie.blit(texto_surface,
                        (self.rect.x + 5,
                         self.rect.y + (self.rect.height - texto_surface.get_height()) // 2))

        # Dibujar triángulo indicador
        pygame.draw.polygon(superficie, (0, 0, 0), [
            (self.rect.x + self.rect.width - 20, self.rect.y + self.rect.height // 2 - 5),
            (self.rect.x + self.rect.width - 10, self.rect.y + self.rect.height // 2 - 5),
            (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height // 2 + 5)
        ])

        # Dibujar opciones si está desplegado
        if self.desplegado:
            for i, opcion in enumerate(self.opciones):
                color = (200, 200, 200) if i % 2 == 0 else (220, 220, 220)
                pygame.draw.rect(superficie, color, self.opcion_rects[i])
                pygame.draw.rect(superficie, (0, 0, 0), self.opcion_rects[i], 1)

                opcion_surface = self.fuente.render(opcion, True, (0, 0, 0))
                superficie.blit(opcion_surface,
                                (self.opcion_rects[i].x + 5,
                                 self.opcion_rects[i].y + (
                                             self.opcion_rects[i].height - opcion_surface.get_height()) // 2))