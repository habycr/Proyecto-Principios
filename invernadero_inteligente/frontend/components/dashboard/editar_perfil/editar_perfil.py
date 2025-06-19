import sys
import re
import pygame
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.services.api_service import APIService


class EditarPerfil:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.usuario = usuario.copy()  # Copia para no modificar el original hasta guardar
        self.usuario_original = usuario.copy()  # Copia del estado original
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 24)
        self.fuente_pequena = pygame.font.Font(None, 20)

        # Variables para campos de texto
        self.campos = {
            'nombre': {
                'valor': usuario.get('nombre', ''),
                'original': usuario.get('nombre', ''),
                'activo': False,
                'rect': pygame.Rect(250, 150, 300, 40),
                'error': '',
                'obligatorio': True
            },
            'email': {
                'valor': usuario.get('email', ''),
                'original': usuario.get('email', ''),
                'activo': False,
                'rect': pygame.Rect(250, 220, 300, 40),
                'error': '',
                'obligatorio': True
            },
            'ubicacion': {
                'valor': usuario.get('ubicacion', ''),
                'original': usuario.get('ubicacion', ''),
                'activo': False,
                'rect': pygame.Rect(250, 290, 300, 40),
                'error': '',
                'obligatorio': False
            }
        }

        # Variables para mostrar mensajes
        self.mostrar_mensaje = False
        self.tiempo_mensaje = 0
        self.texto_mensaje = ""
        self.color_mensaje = (0, 0, 0)

        self.crear_componentes()

    def crear_componentes(self):
        # Título principal
        self.titulo_principal = self.fuente_titulo.render("Editar Perfil", True, (0, 0, 0))

        # Botón Guardar cambios
        self.boton_guardar = Boton(
            self.ancho // 2 - 180,
            self.alto - 120,
            160,
            50,
            "Guardar cambios",
            config.COLOR_BUTTON  # Verde cuando esté activo
        )

        # Botón Cancelar
        self.boton_cancelar = Boton(
            self.ancho // 2 + 20,
            self.alto - 120,
            160,
            50,
            "Cancelar",
            config.COLOR_BUTTON_SECONDARY
        )

    def validar_email(self, email):
        """Valida el formato del email usando regex"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None

    def validar_nombre(self, nombre):
        """Valida que el nombre tenga al menos 3 caracteres"""
        return len(nombre.strip()) >= 3

    def validar_campos(self):
        """Valida todos los campos y actualiza errores"""
        campos_validos = True

        # Validar nombre
        if not self.validar_nombre(self.campos['nombre']['valor']):
            self.campos['nombre']['error'] = "Nombre debe tener al menos 3 caracteres"
            campos_validos = False
        else:
            self.campos['nombre']['error'] = ""

        # Validar email
        if not self.validar_email(self.campos['email']['valor']):
            self.campos['email']['error'] = "Correo inválido"
            campos_validos = False
        else:
            self.campos['email']['error'] = ""

        # Ubicación no requiere validación especial (es opcional)
        self.campos['ubicacion']['error'] = ""

        return campos_validos

    def hay_cambios(self):
        """Verifica si hay cambios respecto a los valores originales"""
        for campo in self.campos.values():
            if campo['valor'] != campo['original']:
                return True
        return False

    def manejar_evento(self, evento):
        # Manejar clics del mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Clic izquierdo
                mouse_pos = evento.pos

                # Activar/desactivar campos de texto
                for nombre_campo, campo in self.campos.items():
                    if campo['rect'].collidepoint(mouse_pos):
                        # Desactivar todos los otros campos
                        for otro_campo in self.campos.values():
                            otro_campo['activo'] = False
                        # Activar el campo clickeado
                        campo['activo'] = True
                    elif not any(c['rect'].collidepoint(mouse_pos) for c in self.campos.values()):
                        # Si no se hizo clic en ningún campo, desactivar todos
                        campo['activo'] = False

                # Manejar botón Guardar
                if self.boton_guardar.rect.collidepoint(mouse_pos):
                    if self.validar_campos() and self.hay_cambios():
                        return self.guardar_cambios()

                # Manejar botón Cancelar
                if self.boton_cancelar.rect.collidepoint(mouse_pos):
                    return "volver_dashboard"

        # Manejar entrada de texto
        if evento.type == pygame.KEYDOWN:
            campo_activo = None
            for nombre_campo, campo in self.campos.items():
                if campo['activo']:
                    campo_activo = campo
                    break

            if campo_activo:
                if evento.key == pygame.K_RETURN:
                    # Validar y posiblemente guardar
                    if self.validar_campos() and self.hay_cambios():
                        return self.guardar_cambios()
                elif evento.key == pygame.K_ESCAPE:
                    campo_activo['activo'] = False
                elif evento.key == pygame.K_BACKSPACE:
                    campo_activo['valor'] = campo_activo['valor'][:-1]
                    # Validar en tiempo real
                    self.validar_campos()
                else:
                    # Agregar carácter si es válido
                    if len(campo_activo['valor']) < 50 and evento.unicode.isprintable():
                        campo_activo['valor'] += evento.unicode
                        # Validar en tiempo real
                        self.validar_campos()

        return None

    def guardar_cambios(self):
        """Intenta guardar los cambios en el perfil"""
        try:
            # Aquí harías la llamada a tu API para actualizar el perfil
            # Por ejemplo: APIService.actualizar_perfil(self.usuario_original['email'], datos_actualizados)

            datos_actualizados = {
                'nombre': self.campos['nombre']['valor'],
                'email': self.campos['email']['valor'],
                'ubicacion': self.campos['ubicacion']['valor']
            }

            respuesta = APIService.actualizar_perfil(self.usuario_original['email'], datos_actualizados)

            if respuesta.get("status") == "success":
                self.texto_mensaje = "Perfil actualizado exitosamente"
                self.color_mensaje = (0, 150, 0)  # Verde
                self.mostrar_mensaje = True
                self.tiempo_mensaje = pygame.time.get_ticks()

                for campo in self.campos.values():
                    campo['original'] = campo['valor']

                return "perfil_actualizado"
            else:
                self.texto_mensaje = respuesta.get("message", "Error al actualizar")
                self.color_mensaje = (150, 0, 0)  # Rojo
                self.mostrar_mensaje = True
                self.tiempo_mensaje = pygame.time.get_ticks()
                return None


        except Exception as e:
            self.texto_mensaje = f"Error al actualizar: {str(e)}"
            self.color_mensaje = (150, 0, 0)  # Rojo
            self.mostrar_mensaje = True
            self.tiempo_mensaje = pygame.time.get_ticks()
            return None

    def dibujar(self, pantalla):
        # Fondo
        pantalla.fill((255, 255, 255))

        # Título principal
        pantalla.blit(self.titulo_principal,
                      (self.ancho // 2 - self.titulo_principal.get_width() // 2, 50))

        # Subtítulo
        subtitulo = self.fuente_normal.render("Modifica tu información personal", True, (100, 100, 100))
        pantalla.blit(subtitulo,
                      (self.ancho // 2 - subtitulo.get_width() // 2, 90))

        # Dibujar campos
        etiquetas = {
            'nombre': 'Nombre completo *',
            'email': 'Correo electrónico *',
            'ubicacion': 'Ubicación'
        }

        for nombre_campo, campo in self.campos.items():
            # Etiqueta del campo
            etiqueta = self.fuente_normal.render(etiquetas[nombre_campo], True, (0, 0, 0))
            pantalla.blit(etiqueta, (campo['rect'].x - 200, campo['rect'].y + 10))

            # Campo de texto
            color_borde = (0, 0, 255) if campo['activo'] else (0, 0, 0)
            if campo['error']:
                color_borde = (255, 0, 0)  # Rojo si hay error

            pygame.draw.rect(pantalla, (255, 255, 255), campo['rect'])
            pygame.draw.rect(pantalla, color_borde, campo['rect'], 2)

            # Texto del campo
            texto_campo = self.fuente_normal.render(campo['valor'], True, (0, 0, 0))
            pantalla.blit(texto_campo, (campo['rect'].x + 10, campo['rect'].y + 10))

            # Cursor si está activo
            if campo['activo']:
                cursor_x = campo['rect'].x + 10 + texto_campo.get_width()
                cursor_y1 = campo['rect'].y + 5
                cursor_y2 = campo['rect'].y + campo['rect'].height - 5
                pygame.draw.line(pantalla, (0, 0, 0), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 1)

            # Mostrar error si existe
            if campo['error']:
                error_texto = self.fuente_pequena.render(campo['error'], True, (255, 0, 0))
                pantalla.blit(error_texto, (campo['rect'].x, campo['rect'].y + campo['rect'].height + 5))

        # Actualizar color del botón Guardar según si hay cambios válidos
        if self.hay_cambios() and self.validar_campos():
            self.boton_guardar.color = config.COLOR_BUTTON  # Verde activo
        else:
            self.boton_guardar.color = (150, 150, 150)  # Gris inactivo

        # Dibujar botones
        self.boton_guardar.dibujar(pantalla)
        self.boton_cancelar.dibujar(pantalla)

        # Mostrar mensaje si es necesario
        if self.mostrar_mensaje:
            if pygame.time.get_ticks() - self.tiempo_mensaje < 3000:  # Mostrar por 3 segundos
                mensaje = self.fuente_normal.render(self.texto_mensaje, True, self.color_mensaje)
                pantalla.blit(mensaje, (self.ancho // 2 - mensaje.get_width() // 2, self.alto - 200))
            else:
                self.mostrar_mensaje = False

        # Nota sobre campos obligatorios
        nota = self.fuente_pequena.render("* Campos obligatorios", True, (100, 100, 100))
        pantalla.blit(nota, (50, self.alto - 50))

    def obtener_datos_actualizados(self):
        """Retorna los datos actualizados del usuario"""
        return {
            'nombre': self.campos['nombre']['valor'],
            'email': self.campos['email']['valor'],
            'ubicacion': self.campos['ubicacion']['valor'],
            'rol': self.usuario_original.get('rol', ''),  # Mantener otros campos
            'numero_serie': self.usuario_original.get('numero_serie', '')
        }