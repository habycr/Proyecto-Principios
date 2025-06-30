# frontend/components/usuarios/registro/elementos/textbox.py
import pygame
from invernadero_inteligente.frontend.config import config


class TextBox:
    def __init__(self, x, y, ancho, alto, texto_inicial="", placeholder="", solo_numeros=False):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.texto = texto_inicial
        self.placeholder = placeholder
        self.solo_numeros = solo_numeros
        self.activo = False
        self.cursor_pos = len(texto_inicial)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.scroll_offset = 0

        # Colores
        self.color_fondo = (255, 255, 255)
        self.color_borde = (200, 200, 200)
        self.color_borde_activo = (100, 150, 255)
        self.color_texto = (0, 0, 0)
        self.color_placeholder = (150, 150, 150)
        self.color_cursor = (0, 0, 0)

        # Fuente
        self.fuente = pygame.font.Font(None, 24)

        # Crear rectángulo
        self.rect = pygame.Rect(x, y, ancho, alto)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            # Verificar si se hizo clic en el textbox
            if self.rect.collidepoint(evento.pos):
                self.activo = True
                # Calcular posición del cursor basada en el clic
                click_x = evento.pos[0] - self.rect.x - 5  # 5 px de padding
                self.cursor_pos = self._calcular_posicion_cursor(click_x)
                return "redraw"
            else:
                self.activo = False
                return "redraw"

        elif evento.type == pygame.KEYDOWN and self.activo:
            if evento.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.texto = self.texto[:self.cursor_pos - 1] + self.texto[self.cursor_pos:]
                    self.cursor_pos -= 1
                    self._ajustar_scroll()
                    return "redraw"

            elif evento.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.texto):
                    self.texto = self.texto[:self.cursor_pos] + self.texto[self.cursor_pos + 1:]
                    self._ajustar_scroll()
                    return "redraw"

            elif evento.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    self._ajustar_scroll()
                    return "redraw"

            elif evento.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.texto):
                    self.cursor_pos += 1
                    self._ajustar_scroll()
                    return "redraw"

            elif evento.key == pygame.K_HOME:
                self.cursor_pos = 0
                self.scroll_offset = 0
                return "redraw"

            elif evento.key == pygame.K_END:
                self.cursor_pos = len(self.texto)
                self._ajustar_scroll()
                return "redraw"

            elif evento.key == pygame.K_RETURN or evento.key == pygame.K_TAB:
                self.activo = False
                return "redraw"

            elif evento.unicode and evento.unicode.isprintable():
                # Filtrar solo números si está configurado
                if self.solo_numeros:
                    if not (evento.unicode.isdigit() or evento.unicode in ".-"):
                        return None

                # Insertar carácter en la posición del cursor
                self.texto = self.texto[:self.cursor_pos] + evento.unicode + self.texto[self.cursor_pos:]
                self.cursor_pos += 1
                self._ajustar_scroll()
                return "redraw"

        return None

    def _calcular_posicion_cursor(self, click_x):
        """Calcula la posición del cursor basada en el clic del mouse"""
        texto_visible = self.texto[self.scroll_offset:]

        for i in range(len(texto_visible) + 1):
            texto_hasta_pos = texto_visible[:i]
            ancho_texto = self.fuente.size(texto_hasta_pos)[0]

            if ancho_texto > click_x:
                return self.scroll_offset + max(0, i - 1)

        return len(self.texto)

    def _ajustar_scroll(self):
        """Ajusta el scroll para mantener el cursor visible"""
        if not self.texto:
            self.scroll_offset = 0
            return

        # Calcular el ancho disponible para texto (restando padding)
        ancho_disponible = self.ancho - 10

        # Texto desde el scroll actual hasta el cursor
        texto_hasta_cursor = self.texto[self.scroll_offset:self.cursor_pos]
        ancho_hasta_cursor = self.fuente.size(texto_hasta_cursor)[0]

        # Si el cursor está fuera del área visible por la derecha
        if ancho_hasta_cursor > ancho_disponible:
            # Mover el scroll hacia la derecha
            while ancho_hasta_cursor > ancho_disponible and self.scroll_offset < self.cursor_pos:
                self.scroll_offset += 1
                texto_hasta_cursor = self.texto[self.scroll_offset:self.cursor_pos]
                ancho_hasta_cursor = self.fuente.size(texto_hasta_cursor)[0]

        # Si el cursor está fuera del área visible por la izquierda
        elif self.cursor_pos < self.scroll_offset:
            self.scroll_offset = self.cursor_pos

    def actualizar(self, dt):
        """Actualiza la animación del cursor"""
        if self.activo:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:  # Parpadeo cada 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False

    def dibujar(self, superficie):
        # Determinar colores según el estado
        color_borde = self.color_borde_activo if self.activo else self.color_borde

        # Dibujar fondo
        pygame.draw.rect(superficie, self.color_fondo, self.rect)

        # Dibujar borde
        pygame.draw.rect(superficie, color_borde, self.rect, 2)

        # Preparar texto para mostrar
        if self.texto:
            texto_mostrar = self.texto[self.scroll_offset:]
            color_texto_actual = self.color_texto
        else:
            texto_mostrar = self.placeholder
            color_texto_actual = self.color_placeholder

        # Recortar texto si es muy largo
        texto_superficie = self.fuente.render(texto_mostrar, True, color_texto_actual)
        ancho_disponible = self.ancho - 10  # 5px padding a cada lado

        if texto_superficie.get_width() > ancho_disponible:
            # Recortar caracteres desde el final hasta que quepa
            while texto_mostrar and self.fuente.size(texto_mostrar)[0] > ancho_disponible:
                texto_mostrar = texto_mostrar[:-1]
            texto_superficie = self.fuente.render(texto_mostrar, True, color_texto_actual)

        # Dibujar texto
        texto_y = self.rect.y + (self.rect.height - texto_superficie.get_height()) // 2
        superficie.blit(texto_superficie, (self.rect.x + 5, texto_y))

        # Dibujar cursor si está activo y visible
        if self.activo and self.cursor_visible and self.texto:
            cursor_x = self._calcular_posicion_cursor_visual()
            cursor_y1 = self.rect.y + 3
            cursor_y2 = self.rect.y + self.rect.height - 3
            pygame.draw.line(superficie, self.color_cursor, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 1)

    def _calcular_posicion_cursor_visual(self):
        """Calcula la posición visual del cursor en pantalla"""
        if self.cursor_pos <= self.scroll_offset:
            return self.rect.x + 5

        texto_hasta_cursor = self.texto[self.scroll_offset:self.cursor_pos]
        ancho_hasta_cursor = self.fuente.size(texto_hasta_cursor)[0]
        return self.rect.x + 5 + ancho_hasta_cursor

    def establecer_texto(self, nuevo_texto):
        """Establece un nuevo texto en el textbox"""
        self.texto = str(nuevo_texto)
        self.cursor_pos = len(self.texto)
        self.scroll_offset = 0
        self._ajustar_scroll()

    def obtener_texto(self):
        """Obtiene el texto actual del textbox"""
        return self.texto

    def limpiar(self):
        """Limpia el contenido del textbox"""
        self.texto = ""
        self.cursor_pos = 0
        self.scroll_offset = 0

    def es_valido_numero(self):
        """Verifica si el texto es un número válido"""
        if not self.texto:
            return False
        try:
            float(self.texto)
            return True
        except ValueError:
            return False

    def obtener_numero(self, valor_defecto=0):
        """Obtiene el texto como número, o el valor por defecto si no es válido"""
        if self.es_valido_numero():
            try:
                return float(self.texto)
            except ValueError:
                return valor_defecto
        return valor_defecto