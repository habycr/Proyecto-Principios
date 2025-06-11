import pygame
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
        self.crear_componentes()
        self.mensaje_error = None
        self.usuario_autenticado = None

    def crear_componentes(self):
        x_pos = self.ancho // 2 - 150
        self.campo_email = InputBox(x_pos, 200, 300, 40, "Correo electrónico")
        self.campo_password = PasswordBox(x_pos, 270, 300, 40, "Contraseña")
        self.boton_volver = Boton(x_pos - 50, 350, 120, 40, "Volver", config.COLOR_BUTTON_SECONDARY)
        self.boton_login = Boton(x_pos + 180, 350, 170, 40, "Iniciar sesión", config.COLOR_BUTTON)

    def manejar_evento(self, evento):
        # Pasar eventos a los campos
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
        # Validaciones básicas
        if not self.campo_email.texto or not self.campo_password.texto:
            return "Complete todos los campos"

        # Validación básica de email
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
            # Aquí podrías redirigir al dashboard
        else:
            self.mensaje_error = respuesta.get("message", "Error desconocido al iniciar sesión")
            self.usuario_autenticado = None

    def dibujar(self, superficie):
        titulo = self.fuente.render("Inicio de Sesión", True, (0, 0, 0))
        superficie.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 100))

        self.campo_email.dibujar(superficie)
        self.campo_password.dibujar(superficie)
        self.boton_volver.dibujar(superficie)
        self.boton_login.dibujar(superficie)

        if self.mensaje_error:
            texto_error = self.fuente_chica.render(self.mensaje_error, True, config.COLOR_ERROR)
            superficie.blit(texto_error, (self.ancho // 2 - texto_error.get_width() // 2, 420))

        if hasattr(self, 'mensaje_exito') and self.mensaje_exito:
            texto_exito = self.fuente_chica.render(self.mensaje_exito, True, config.COLOR_SUCCESS)
            superficie.blit(texto_exito, (self.ancho // 2 - texto_exito.get_width() // 2, 420))

