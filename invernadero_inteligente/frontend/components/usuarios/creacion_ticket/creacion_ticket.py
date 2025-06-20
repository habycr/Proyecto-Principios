# frontend/screens/creacion_ticket.py
import pygame
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.services.api_service import APIService
from invernadero_inteligente.frontend.config import config

class CreacionTicket:
    def __init__(self, ancho, alto, usuario):
        self.ancho = ancho
        self.alto = alto
        self.usuario = usuario
        self.fuente = pygame.font.Font(None, 28)
        self.fuente_pequena = pygame.font.Font(None, 22)
        self.scroll_offset = 0
        self.altura_item = 40
        self.area_scroll = pygame.Rect(250, 120, 300, 150)  # área visible de la lista de dispositivos
        self.item_rects = []  # Se actualiza en cada dibujado

        numero_serie = usuario.get('numero_serie', [])
        if isinstance(numero_serie, list):
            self.dispositivos = [s.strip() for s in numero_serie if s.strip()]
        elif isinstance(numero_serie, str):
            self.dispositivos = [s.strip() for s in numero_serie.split(',') if s.strip()]
        else:
            self.dispositivos = []

        self.dispositivo_seleccionado = ''
        self.asunto = ''
        self.descripcion = ''
        self.errores = {'dispositivo': '', 'asunto': '', 'descripcion': ''}

        self.mensaje_envio = ''
        self.mostrar_mensaje = False
        self.boton_refrescar = Boton(
            x=580,
            y=120,
            ancho=150,
            alto=40,
            texto="Refrescar",
            color=(100, 170, 255)
        )

        self.rects = {
            'dropdown': pygame.Rect(250, 120, 300, 40),
            'asunto': pygame.Rect(250, 190, 300, 40),
            'descripcion': pygame.Rect(250, 260, 500, 120),
        }
        self.activo = {'dropdown': False, 'asunto': False, 'descripcion': False}

        self.boton_volver = Boton(
            x=20,
            y=20,
            ancho=120,
            alto=40,
            texto="Volver",
            color=(200, 100, 100)  # rojo claro
        )
        self.boton_enviar = Boton(350, alto - 100, 180, 50, "Enviar Ticket", config.COLOR_BUTTON)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = evento.pos

            # Volver
            if self.boton_volver.rect.collidepoint(pos):
                return "volver_dashboard"

            # Botón enviar
            if self.validar():
                data = {
                    "email": self.usuario['email'],
                    "dispositivo": self.dispositivo_seleccionado,
                    "asunto": self.asunto,
                    "descripcion": self.descripcion
                }
                response = APIService.crear_ticket(data)
                if response.get("status") == "success":
                    self.mensaje_envio = "Ticket enviado correctamente"
                    self.mostrar_mensaje = True
                    self.limpiar_formulario()
                else:
                    self.mensaje_envio = f"Error: {response.get('message', 'Error desconocido')}"
                    self.mostrar_mensaje = True

            # Botón refrescar
            if self.boton_refrescar.rect.collidepoint(pos):
                self.refrescar_dispositivos()
                return

            # Click en algún dispositivo visible
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(pos):
                    self.dispositivo_seleccionado = self.dispositivos[i]
                    break

            # Activar campos de texto
            self.activo['asunto'] = self.rects['asunto'].collidepoint(pos)
            self.activo['descripcion'] = self.rects['descripcion'].collidepoint(pos)

        elif evento.type == pygame.MOUSEWHEEL:
            # Scroll del mouse
            max_scroll = max(0, len(self.dispositivos) * self.altura_item - self.area_scroll.height)
            self.scroll_offset -= evento.y * 20  # evento.y = 1 o -1
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        elif evento.type == pygame.KEYDOWN:
            if self.activo['asunto']:
                if evento.key == pygame.K_BACKSPACE:
                    self.asunto = self.asunto[:-1]
                elif evento.key != pygame.K_RETURN:
                    if len(self.asunto) < 100:
                        self.asunto += evento.unicode
            elif self.activo['descripcion']:
                if evento.key == pygame.K_BACKSPACE:
                    self.descripcion = self.descripcion[:-1]
                elif evento.key != pygame.K_RETURN:
                    self.descripcion += evento.unicode

    def validar(self):
        self.errores = {'dispositivo': '', 'asunto': '', 'descripcion': ''}
        valido = True

        if not self.dispositivo_seleccionado:
            self.errores['dispositivo'] = "Seleccione un dispositivo"
            valido = False

        if len(self.asunto.strip()) == 0:
            self.errores['asunto'] = "Asunto requerido"
            valido = False

        if len(self.descripcion.strip()) < 20:
            self.errores['descripcion'] = "Describa el problema (mín. 20 caracteres)"
            valido = False

        return valido

    def limpiar_formulario(self):
        self.dispositivo_seleccionado = ''
        self.asunto = ''
        self.descripcion = ''
        self.errores = {'dispositivo': '', 'asunto': '', 'descripcion': ''}

    def dibujar(self, pantalla):
        pantalla.fill((255, 255, 255))
        titulo = self.fuente.render("Crear Ticket de Soporte", True, (0, 0, 0))
        pantalla.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 30))

        # Posiciones reajustadas
        self.area_scroll.y = 100
        self.boton_refrescar.rect.y = self.area_scroll.y
        self.boton_refrescar.rect.x = self.area_scroll.right + 10

        self.rects['asunto'].y = self.area_scroll.bottom + 30
        self.rects['descripcion'].y = self.rects['asunto'].bottom + 30

        etiquetas = {
            'asunto': "Asunto *",
            'descripcion': "Descripción del problema *"
        }

        # === ÁREA SCROLLABLE DE DISPOSITIVOS ===
        etiqueta_dispositivo = self.fuente.render("Dispositivo *", True, (0, 0, 0))
        pantalla.blit(etiqueta_dispositivo, (self.area_scroll.x - 220, self.area_scroll.y + 10))
        pygame.draw.rect(pantalla, (230, 230, 230), self.area_scroll)  # fondo
        pygame.draw.rect(pantalla, (0, 0, 0), self.area_scroll, 2)  # borde

        self.item_rects = []
        for i, dispositivo in enumerate(self.dispositivos):
            item_y = self.area_scroll.y + i * self.altura_item - self.scroll_offset
            if self.area_scroll.top <= item_y <= self.area_scroll.bottom - self.altura_item:
                item_rect = pygame.Rect(self.area_scroll.x, item_y, self.area_scroll.width, self.altura_item)
                color = (180, 230, 180) if dispositivo == self.dispositivo_seleccionado else (255, 255, 255)
                pygame.draw.rect(pantalla, color, item_rect)
                pygame.draw.rect(pantalla, (0, 0, 0), item_rect, 1)
                texto = self.fuente.render(dispositivo, True, (0, 0, 0))
                pantalla.blit(texto, (item_rect.x + 10, item_rect.y + 10))
                self.item_rects.append(item_rect)

        # Mostrar error si no hay dispositivo seleccionado
        if self.errores['dispositivo']:
            error = self.fuente_pequena.render(self.errores['dispositivo'], True, (255, 0, 0))
            pantalla.blit(error, (self.area_scroll.x, self.area_scroll.bottom + 5))

        # Dibujar botón refrescar
        self.boton_refrescar.dibujar(pantalla)

        # === CAMPOS DE TEXTO ===
        for campo in ['asunto', 'descripcion']:
            rect = self.rects[campo]
            etiqueta = self.fuente.render(etiquetas[campo], True, (0, 0, 0))
            pantalla.blit(etiqueta, (rect.x - 220, rect.y + 10))
            pygame.draw.rect(pantalla, (255, 255, 255), rect)
            pygame.draw.rect(pantalla, (0, 0, 0), rect, 2)

            texto = self.asunto if campo == 'asunto' else self.descripcion
            texto_render = self.fuente.render(texto, True, (0, 0, 0))
            pantalla.blit(texto_render, (rect.x + 10, rect.y + 8))

            if self.errores[campo]:
                error = self.fuente_pequena.render(self.errores[campo], True, (255, 0, 0))
                pantalla.blit(error, (rect.x, rect.y + rect.height + 5))

        # Dibujar botones
        self.boton_enviar.dibujar(pantalla)
        self.boton_volver.dibujar(pantalla)

        # Mostrar mensaje de éxito
        if self.mostrar_mensaje:
            mensaje = self.fuente.render(self.mensaje_envio, True, (0, 150, 0))
            pantalla.blit(mensaje, (self.ancho // 2 - mensaje.get_width() // 2, self.alto - 150))

    def refrescar_dispositivos(self):
        from invernadero_inteligente.frontend.services.api_service import APIService
        response = APIService.obtener_usuario(self.usuario['email'])
        print("Respuesta API refrescar_dispositivos:", response)  # 👈 DEBUG
        if response.get("status") == "success":
            usuario_actualizado = response.get("usuario", {})
            numero_serie = usuario_actualizado.get('numero_serie', [])
            if isinstance(numero_serie, list):
                self.dispositivos = [s.strip() for s in numero_serie if s.strip()]
            elif isinstance(numero_serie, str):
                self.dispositivos = [s.strip() for s in numero_serie.split(',') if s.strip()]
            else:
                self.dispositivos = []
