import pygame
from .elementos.input_box import InputBox
from .elementos.boton import Boton
from .elementos.dropdown import Dropdown
from .elementos.password_box import PasswordBox
from invernadero_inteligente.frontend.services.api_service import APIService  # Ajusta la ruta según tu estructura


class RegistroUsuario:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente = pygame.font.Font(None, 32)
        self.fuente_chica = pygame.font.Font(None, 24)
        self.crear_componentes()
        self.mensaje_error = None
        self.mensaje_exito = None

    def crear_componentes(self):
        x_pos = self.ancho // 2 - 150

        # Campos de usuario
        self.campo_nombre = InputBox(x_pos, 120, 300, 40, "Nombre completo*")
        self.campo_email = InputBox(x_pos, 190, 300, 40, "Correo electrónico*")
        self.campo_password = PasswordBox(x_pos, 260, 300, 40, "Contraseña*")
        self.campo_confirm_password = PasswordBox(x_pos, 330, 300, 40, "Confirmar contraseña*")
        self.campo_telefono = InputBox(x_pos, 400, 300, 40, "Teléfono (opcional)")

        # Campos de dispositivo
        self.campo_numero_serie = InputBox(x_pos, 470, 300, 40, "Número de serie del dispositivo*")
        self.campo_ubicacion = InputBox(x_pos, 540, 300, 40, "Ubicación del dispositivo")

        # Dropdown para rol
        roles = ["Seleccionar rol...", "Administrador", "Usuario final", "Técnico"]
        self.dropdown_rol = Dropdown(x_pos, 610, 300, 40, roles)

        # Botones
        self.boton_volver = Boton(x_pos - 50, 670, 120, 40, "Volver", (200, 200, 200))
        self.boton_registrar = Boton(x_pos + 180, 670, 170, 40, "Registrar cuenta", (100, 200, 100))

    def manejar_evento(self, evento):
        # Pasar eventos a todos los campos
        for campo in [self.campo_nombre, self.campo_email, self.campo_password,
                     self.campo_confirm_password, self.campo_telefono,
                     self.campo_numero_serie, self.campo_ubicacion]:
            campo.manejar_evento(evento)

        self.dropdown_rol.manejar_evento(evento)

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_registrar.rect.collidepoint(evento.pos):
                self.registrar_usuario()
            elif self.boton_volver.rect.collidepoint(evento.pos):
                self.limpiar_formulario()

    def limpiar_formulario(self):
        """Reinicia todos los campos del formulario"""
        self.campo_nombre.texto = ""
        self.campo_email.texto = ""
        self.campo_password.texto = ""
        self.campo_confirm_password.texto = ""
        self.campo_telefono.texto = ""
        self.campo_numero_serie.texto = ""
        self.campo_ubicacion.texto = ""
        self.dropdown_rol.seleccion_actual = "Seleccionar rol..."
        self.mensaje_error = None
        self.mensaje_exito = None

    def validar_formulario(self):
        # Validaciones básicas
        if not all([
            self.campo_nombre.texto,
            self.campo_email.texto,
            self.campo_password.texto,
            self.campo_numero_serie.texto,
            self.dropdown_rol.seleccion_actual != "Seleccionar rol..."
        ]):
            return "Complete todos los campos obligatorios"

        # Validación básica de email (puedes mejorarla)
        if "@" not in self.campo_email.texto or "." not in self.campo_email.texto.split("@")[-1]:
            return "Ingrese un email válido"

        # Resto de validaciones...
        if self.campo_password.texto != self.campo_confirm_password.texto:
            return "Las contraseñas no coinciden"

        if len(self.campo_password.texto) < 8:
            return "La contraseña debe tener al menos 8 caracteres"

        # Validación básica de número de serie
        if len(self.campo_numero_serie.texto) < 5:
            return "Número de serie inválido (mínimo 5 caracteres)"

        return None

    def registrar_usuario(self):
        error = self.validar_formulario()
        if error:
            self.mensaje_error = error
            self.mensaje_exito = None
            return

        datos_usuario = {
            "nombre": self.campo_nombre.texto,
            "email": self.campo_email.texto,
            "password": self.campo_password.texto,
            "rol": self.dropdown_rol.seleccion_actual,
            "telefono": self.campo_telefono.texto,
            "numero_serie": self.campo_numero_serie.texto,
            "ubicacion": self.campo_ubicacion.texto
        }

        respuesta = APIService.registrar_usuario(datos_usuario)

        if respuesta.get("status") == "success":
            self.mensaje_exito = respuesta["message"]
            self.limpiar_formulario()
        else:
            self.mensaje_error = respuesta.get("message", "Error desconocido al registrar")

    def dibujar(self, superficie):
        # Título
        titulo = self.fuente.render("Registro de Usuario", True, (0, 0, 0))
        superficie.blit(titulo, (self.ancho // 2 - titulo.get_width() // 2, 50))

        # Campos
        for campo in [self.campo_nombre, self.campo_email, self.campo_password,
                     self.campo_confirm_password, self.campo_telefono,
                     self.campo_numero_serie, self.campo_ubicacion]:
            campo.dibujar(superficie)

        self.dropdown_rol.dibujar(superficie)

        # Botones
        self.boton_volver.dibujar(superficie)
        self.boton_registrar.dibujar(superficie)

        # Mensajes
        if self.mensaje_error:
            texto_error = self.fuente_chica.render(self.mensaje_error, True, (200, 0, 0))
            superficie.blit(texto_error, (self.ancho // 2 - texto_error.get_width() // 2, 720))

        if self.mensaje_exito:
            texto_exito = self.fuente_chica.render(self.mensaje_exito, True, (0, 150, 0))
            superficie.blit(texto_exito, (self.ancho // 2 - texto_exito.get_width() // 2, 720))