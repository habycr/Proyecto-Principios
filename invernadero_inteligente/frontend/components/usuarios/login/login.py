import pygame
import os
from invernadero_inteligente.frontend.config import config
from components.usuarios.registro.elementos.input_box import InputBox
from components.usuarios.registro.elementos.boton import Boton
from components.usuarios.registro.elementos.password_box import PasswordBox
from invernadero_inteligente.frontend.services.api_service import APIService


class Login:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente = pygame.font.Font(None, 32)
        self.fuente_chica = pygame.font.Font(None, 24)

        # Cargar la imagen
        self.imagen = self.imagen = Login.cargar_imagen()

        self.crear_componentes()
        self.mensaje_error = None
        self.usuario_autenticado = None

    @staticmethod
    def cargar_imagen():
        """Carga y escala la imagen para el login"""
        try:
            ruta_imagen = os.path.join("Proyecto-Principios/frontend/components/usuarios/registro/elementos/logo/logo.png")

            # Cargar imagen
            imagen = pygame.image.load(ruta_imagen)

            # Escalar la imagen (ajusta estos valores según necesites)
            ancho_imagen = 300  # Ancho deseado en píxeles
            alto_imagen = 150  # Alto deseado en píxeles
            imagen = pygame.transform.scale(imagen, (ancho_imagen, alto_imagen))

            return imagen
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")
            return None

    def crear_componentes(self):
        x_pos = self.ancho // 2 - 150
        self.campo_email = InputBox(x_pos, 200, 300, 40, "Correo electrónico")
        self.campo_password = PasswordBox(x_pos, 270, 300, 40, "Contraseña")
        self.boton_volver = Boton(x_pos - 50, 350, 120, 40, "Volver", config.COLOR_BUTTON_SECONDARY)
        self.boton_login = Boton(x_pos + 180, 350, 170, 40, "Iniciar sesión", config.COLOR_BUTTON)

    def manejar_evento(self, evento):
        self.campo_email.manejar_evento(evento)
        self.campo_password.manejar_evento(evento)

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_login.rect.collidepoint(evento.pos):
                self.iniciar_sesion()
            elif self.boton_volver.rect.collidepoint(evento.pos):
                self.limpiar_formulario()

    def limpiar_formulario(self):
        """Reinicia todos los campos del formulario"""
        self.campo_email.texto = ""
        self.campo_password.texto = ""
        self.mensaje_error = None

    def validar_formulario(self):
        if not self.campo_email.texto or not self.campo_password.texto:
            return "Complete todos los campos"

        if "@" not in self.campo_email.texto or "." not in self.campo_email.texto.split("@")[-1]:
            return "Ingrese un email válido"

        return None

    def iniciar_sesion(self):
        error = self.validar_formulario()
        if error:
            self.mensaje_error = error
            self.mensaje_exito = None
            return

        credenciales = {
            "email": self.campo_email.texto,
            "password": self.campo_password.texto
        }

        respuesta = APIService.iniciar_sesion(credenciales)

        if respuesta.get("status") == "success":
            self.usuario_autenticado = respuesta.get("user")
            self.mensaje_exito = "Inicio de sesión exitoso"
            self.mensaje_error = None
        else:
            self.mensaje_error = respuesta.get("message", "Error desconocido al iniciar sesión")
            self.usuario_autenticado = None

    def dibujar(self, superficie):
        # Fondo blanco
        superficie.fill((255, 255, 255))

        # Título
        titulo = self.fuente.render("Inicio de Sesión", True, (0, 0, 0))
        superficie.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 100))

        # Componentes del formulario
        self.campo_email.dibujar(superficie)
        self.campo_password.dibujar(superficie)
        self.boton_volver.dibujar(superficie)
        self.boton_login.dibujar(superficie)

        # Mensajes de error/éxito
        if self.mensaje_error:
            texto_error = self.fuente_chica.render(self.mensaje_error, True, config.COLOR_ERROR)
            superficie.blit(texto_error, (self.ancho // 2 - texto_error.get_width() // 2, 420))

        if hasattr(self, 'mensaje_exito') and self.mensaje_exito:
            texto_exito = self.fuente_chica.render(self.mensaje_exito, True, config.COLOR_SUCCESS)
            superficie.blit(texto_exito, (self.ancho // 2 - texto_exito.get_width() // 2, 420))

        # Dibujar imagen en la parte inferior
        if self.imagen:
            # Posición de la imagen (centrada horizontalmente, 50px desde el fondo)
            pos_x = self.ancho // 2 - self.imagen.get_width() // 2
            pos_y = self.alto - self.imagen.get_height() - 50
            superficie.blit(self.imagen, (pos_x, pos_y))
