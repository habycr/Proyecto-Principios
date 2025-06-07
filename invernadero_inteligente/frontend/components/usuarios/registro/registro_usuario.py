# frontend/components/usuario/registro/registro_usuario.py
# frontend/components/usuario/registro/registro_usuario.py
import pygame
from .elementos.input_box import InputBox
from .elementos.boton import Boton
from .elementos.dropdown import Dropdown
from .elementos.password_box import PasswordBox


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

        # Campos de dispositivo (RF31)
        self.campo_numero_serie = InputBox(x_pos, 470, 300, 40, "Número de serie del dispositivo*")
        self.campo_ubicacion = InputBox(x_pos, 540, 300, 40, "Ubicación del dispositivo")

        # Dropdown para rol (RF31)
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
                self.limpiar_formulario()  # <-- Ahora este método existe

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
        # Validar campos obligatorios (RF01)
        if not all([
            self.campo_nombre.texto,
            self.campo_email.texto,
            self.campo_password.texto,
            self.campo_numero_serie.texto,
            self.dropdown_rol.seleccion_actual != "Seleccionar rol..."
        ]):
            return "Complete todos los campos obligatorios"

        # Validar contraseña (RNF02)
        if self.campo_password.texto != self.campo_confirm_password.texto:
            return "Las contraseñas no coinciden"

        if len(self.campo_password.texto) < 8:
            return "La contraseña debe tener al menos 8 caracteres"

        # Validar número de serie (RF02, RF29)
        if not self.validar_numero_serie(self.campo_numero_serie.texto):
            return "Número de serie inválido"

        return None

    def validar_numero_serie(self, numero_serie):
        # Lógica para validar con el backend (RF02)
        # Por ahora simulamos validación básica
        return len(numero_serie) >= 5  # Ejemplo: "INV-12345"

    def registrar_usuario(self):
        error = self.validar_formulario()
        if error:
            self.mensaje_error = error
            self.mensaje_exito = None
            return

        # Simular registro exitoso (RF01, RF31)
        self.mensaje_exito = f"Usuario {self.campo_nombre.texto} registrado exitosamente"
        self.mensaje_error = None

        # Aquí iría la lógica para:
        # 1. Encriptar contraseña (RNF02)
        # 2. Enviar datos al backend (RF34)
        # 3. Crear tarjeta de equipo (RF29)
        # 4. Asociar dispositivo (RF31)

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