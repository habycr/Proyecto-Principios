# frontend/components/dispositivos/registro/registro_dispositivo.py
import pygame
from .elementos.input_box import InputBox
from .elementos.boton import Boton
from .elementos.dropdown import Dropdown


class RegistroDispositivo:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana

        # Fuente
        self.fuente = pygame.font.Font(None, 32)
        self.fuente_chica = pygame.font.Font(None, 24)

        # Componentes
        self.crear_componentes()

        # Estado
        self.mensaje_error = None
        self.mensaje_exito = None

    def crear_componentes(self):
        # Título
        self.titulo = self.fuente.render("Registrar Dispositivo", True, (0, 0, 0))

        # Campos de entrada
        x_pos = self.ancho // 2 - 150
        self.campo_numero_serie = InputBox(x_pos, 150, 300, 40, "Número de serie*")
        self.campo_ubicacion = InputBox(x_pos, 220, 300, 40, "Ubicación*")
        self.campo_descripcion = InputBox(x_pos, 290, 300, 40, "Descripción (opcional)")

        # Dropdown para usuario
        opciones_usuarios = ["Seleccionar usuario...", "Usuario 1", "Usuario 2", "Nuevo usuario"]
        self.dropdown_usuario = Dropdown(x_pos, 360, 300, 40, opciones_usuarios)

        # Botones
        self.boton_cancelar = Boton(x_pos, 430, 140, 40, "Cancelar", (200, 200, 200))
        self.boton_registrar = Boton(x_pos + 160, 430, 140, 40, "Registrar", (100, 200, 100))

    def manejar_evento(self, evento):
        self.campo_numero_serie.manejar_evento(evento)
        self.campo_ubicacion.manejar_evento(evento)
        self.campo_descripcion.manejar_evento(evento)
        self.dropdown_usuario.manejar_evento(evento)

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_registrar.rect.collidepoint(evento.pos):
                self.registrar_dispositivo()
            elif self.boton_cancelar.rect.collidepoint(evento.pos):
                self.limpiar_formulario()

    def registrar_dispositivo(self):
        # Validar campos obligatorios
        if (not self.campo_numero_serie.texto or
                not self.campo_ubicacion.texto or
                self.dropdown_usuario.seleccion_actual == "Seleccionar usuario..."):
            self.mensaje_error = "Complete todos los campos obligatorios"
            self.mensaje_exito = None
            return

        # Aquí iría la lógica para enviar los datos al backend
        # Por ahora simulamos un registro exitoso
        self.mensaje_exito = f"Dispositivo {self.campo_numero_serie.texto} registrado exitosamente"
        self.mensaje_error = None

        # En una implementación real, aquí se llamaría al backend para:
        # 1. Validar número de serie único (RF02)
        # 2. Crear tarjeta de equipo (RF29)
        # 3. Asociar usuario (RF31)
        # 4. Almacenar en base de datos (RF34)

    def limpiar_formulario(self):
        self.campo_numero_serie.texto = ""
        self.campo_ubicacion.texto = ""
        self.campo_descripcion.texto = ""
        self.dropdown_usuario.seleccion_actual = "Seleccionar usuario..."
        self.mensaje_error = None
        self.mensaje_exito = None

    def dibujar(self, superficie):
        # Dibujar título
        superficie.blit(self.titulo, (self.ancho // 2 - self.titulo.get_width() // 2, 80))

        # Dibujar campos
        self.campo_numero_serie.dibujar(superficie)
        self.campo_ubicacion.dibujar(superficie)
        self.campo_descripcion.dibujar(superficie)
        self.dropdown_usuario.dibujar(superficie)

        # Dibujar botones
        self.boton_cancelar.dibujar(superficie)
        self.boton_registrar.dibujar(superficie)

        # Dibujar mensajes
        if self.mensaje_error:
            texto_error = self.fuente_chica.render(self.mensaje_error, True, (200, 0, 0))
            superficie.blit(texto_error, (self.ancho // 2 - texto_error.get_width() // 2, 490))

        if self.mensaje_exito:
            texto_exito = self.fuente_chica.render(self.mensaje_exito, True, (0, 150, 0))
            superficie.blit(texto_exito, (self.ancho // 2 - texto_exito.get_width() // 2, 490))