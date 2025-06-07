# frontend/components/usuario/registro/elementos/password_box.py
import pygame
from .input_box import InputBox  # Importar la clase padre desde el módulo relativo


class PasswordBox(InputBox):  # Ahora sí reconoce InputBox
    def __init__(self, x, y, ancho, alto, texto_placeholder=""):
        super().__init__(x, y, ancho, alto, texto_placeholder)
        self.mostrar_texto = False  # Para alternar entre **** y texto plano
        self.icono_ojo = pygame.Surface((20, 15))  # Superficie para el icono de ojo
        self.icono_ojo.fill((200, 200, 200))  # Fondo gris
        pygame.draw.circle(self.icono_ojo, (80, 80, 80), (10, 7), 5)  # Ojo simple

    def dibujar(self, superficie):
        # Dibujar el rectángulo base (comportamiento de InputBox)
        pygame.draw.rect(superficie, self.color, self.rect, 2)

        # Texto a mostrar (asteriscos o texto plano)
        texto_mostrado = "*" * len(self.texto) if not self.mostrar_texto else self.texto

        # Renderizar texto o placeholder
        if texto_mostrado:
            texto_surface = self.fuente.render(texto_mostrado, True, self.color_texto)
        else:
            texto_surface = self.fuente.render(self.texto_placeholder, True, pygame.Color('gray'))

        superficie.blit(texto_surface, (self.rect.x + 5, self.rect.y + 5))

        # Botón para mostrar/ocultar contraseña (mejorado)
        boton_ojo = pygame.Rect(
            self.rect.x + self.rect.width - 35,
            self.rect.y + (self.rect.height - 15) // 2,
            30, 15
        )
        superficie.blit(self.icono_ojo, boton_ojo)

        # Cursor si está activo
        if self.activo:
            cursor_x = self.rect.x + 5 + texto_surface.get_width()
            pygame.draw.line(superficie, self.color_texto,
                             (cursor_x, self.rect.y + 5),
                             (cursor_x, self.rect.y + self.rect.height - 5))

    def manejar_evento(self, evento):
        super().manejar_evento(evento)  # Comportamiento base de InputBox
        if evento.type == pygame.MOUSEBUTTONDOWN:
            boton_ojo = pygame.Rect(
                self.rect.x + self.rect.width - 35,
                self.rect.y + (self.rect.height - 15) // 2,
                30, 15
            )
            if boton_ojo.collidepoint(evento.pos):
                self.mostrar_texto = not self.mostrar_texto