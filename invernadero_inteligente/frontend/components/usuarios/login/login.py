import pygame
import os
import requests
from io import BytesIO
from invernadero_inteligente.frontend.config import config
from invernadero_inteligente.diseno import EstiloLabel, Colores, Fuentes, Dimensiones, EstiloTarjeta
from components.usuarios.registro.elementos.input_box import InputBox
from components.usuarios.registro.elementos.boton import Boton
from components.usuarios.registro.elementos.password_box import PasswordBox
from invernadero_inteligente.frontend.services.api_service import APIService


class Login:
    def __init__(self, ancho_ventana, alto_ventana):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.fuente = pygame.font.SysFont(Fuentes.GENERAL[0], Fuentes.TITULO_PRINCIPAL[1])
        self.fuente_chica = pygame.font.SysFont(Fuentes.GENERAL[0], Fuentes.NORMAL[1])
        self.fuente_subtitulo = pygame.font.SysFont(Fuentes.GENERAL[0], Fuentes.SUBTITULO[1])

        # Cargar la imagen
        self.imagen = Login.cargar_imagen_desde_github()

        self.crear_componentes()
        self.mensaje_error = None
        self.usuario_autenticado = None

    @staticmethod
    def cargar_imagen_desde_github():
        url = "https://raw.githubusercontent.com/habycr/Proyecto-Principios/6b91ab4a49c35c8810bff80b7b1b537ab67ffff6/invernadero_inteligente/frontend/components/usuarios/registro/elementos/logo/logo.png"
        try:
            response = requests.get(url)
            response.raise_for_status()
            imagen = pygame.image.load(BytesIO(response.content))
            return imagen
        except Exception as e:
            print(f"Error al cargar imagen desde GitHub: {e}")
            return None

    def crear_componentes(self):
        # Panel central más amplio y centrado
        panel_ancho = 400
        panel_alto = 380
        panel_x = self.ancho // 2 - panel_ancho // 2
        panel_y = self.alto // 2 - panel_alto // 2 - 20

        # Elementos dentro del panel con mejor espaciado
        x_pos = panel_x + Dimensiones.MARGEN_GRANDE
        input_ancho = panel_ancho - (Dimensiones.MARGEN_GRANDE * 2)

        # Campos de entrada con mayor altura y espaciado
        self.campo_email = InputBox(x_pos, panel_y + 80, input_ancho, 45, "Correo electrónico")
        self.campo_password = PasswordBox(x_pos, panel_y + 150, input_ancho, 45, "Contraseña")

        # Botones con mejor distribución y tamaños del sistema de diseño
        boton_ancho = (input_ancho - Dimensiones.MARGEN_NORMAL) // 2
        self.boton_volver = Boton(x_pos, panel_y + 220, boton_ancho, 50, "Volver", Colores.SUPERFICIE)
        self.boton_login = Boton(x_pos + boton_ancho + Dimensiones.MARGEN_NORMAL, panel_y + 220, boton_ancho, 50,
                                 "Iniciar sesión", Colores.PRIMARIO)

        # Guardar dimensiones del panel para dibujar el fondo
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)

    def manejar_evento(self, evento):
        self.campo_email.manejar_evento(evento)
        self.campo_password.manejar_evento(evento)

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.boton_login.rect.collidepoint(evento.pos):
                self.iniciar_sesion()
            elif self.boton_volver.rect.collidepoint(evento.pos):
                self.limpiar_formulario()

    def limpiar_formulario(self):
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

    def dibujar_panel_fondo(self, superficie):
        """Dibuja el panel de fondo con estilo de tarjeta"""
        # Sombra sutil
        sombra_rect = pygame.Rect(self.panel_rect.x + 4, self.panel_rect.y + 4,
                                  self.panel_rect.width, self.panel_rect.height)
        pygame.draw.rect(superficie, (200, 200, 200, 50), sombra_rect, border_radius=Dimensiones.RADIO_TARJETA)

        # Panel principal
        pygame.draw.rect(superficie, Colores.SUPERFICIE, self.panel_rect, border_radius=Dimensiones.RADIO_TARJETA)
        pygame.draw.rect(superficie, Colores.BORDE, self.panel_rect, width=2, border_radius=Dimensiones.RADIO_TARJETA)

    def dibujar_encabezado(self, superficie):
        """Dibuja el encabezado con título y subtítulo"""
        # Título principal
        titulo = self.fuente.render("Invernadero Inteligente", True, Colores.PRIMARIO)
        titulo_x = self.ancho // 2 - titulo.get_width() // 2
        titulo_y = self.panel_rect.y - 80
        superficie.blit(titulo, (titulo_x, titulo_y))

        # Subtítulo
        subtitulo = self.fuente_subtitulo.render("Inicio de Sesión", True, Colores.TEXTO_PRIMARIO)
        subtitulo_x = self.ancho // 2 - subtitulo.get_width() // 2
        subtitulo_y = self.panel_rect.y + Dimensiones.MARGEN_NORMAL
        superficie.blit(subtitulo, (subtitulo_x, subtitulo_y))

        # Línea decorativa bajo el subtítulo
        linea_y = subtitulo_y + 35
        linea_start = self.panel_rect.x + Dimensiones.MARGEN_GRANDE
        linea_end = self.panel_rect.x + self.panel_rect.width - Dimensiones.MARGEN_GRANDE
        pygame.draw.line(superficie, Colores.PRIMARIO, (linea_start, linea_y), (linea_end, linea_y), 2)

    def dibujar_mensajes(self, superficie):
        """Dibuja mensajes de error o éxito con mejor estilo"""
        mensaje_y = self.panel_rect.y + self.panel_rect.height + Dimensiones.MARGEN_NORMAL

        if self.mensaje_error:
            # Fondo del mensaje de error
            texto_error = self.fuente_chica.render(self.mensaje_error, True, Colores.ERROR)
            mensaje_ancho = texto_error.get_width() + Dimensiones.MARGEN_NORMAL * 2
            mensaje_alto = texto_error.get_height() + Dimensiones.MARGEN_PEQUENO * 2
            mensaje_x = self.ancho // 2 - mensaje_ancho // 2

            mensaje_rect = pygame.Rect(mensaje_x, mensaje_y, mensaje_ancho, mensaje_alto)
            pygame.draw.rect(superficie, (255, 235, 238), mensaje_rect, border_radius=Dimensiones.RADIO_BORDE)
            pygame.draw.rect(superficie, Colores.ERROR, mensaje_rect, width=1, border_radius=Dimensiones.RADIO_BORDE)

            # Texto del error
            texto_x = mensaje_x + Dimensiones.MARGEN_NORMAL
            texto_y = mensaje_y + Dimensiones.MARGEN_PEQUENO
            superficie.blit(texto_error, (texto_x, texto_y))

        if hasattr(self, 'mensaje_exito') and self.mensaje_exito:
            # Fondo del mensaje de éxito
            texto_exito = self.fuente_chica.render(self.mensaje_exito, True, Colores.EXITO)
            mensaje_ancho = texto_exito.get_width() + Dimensiones.MARGEN_NORMAL * 2
            mensaje_alto = texto_exito.get_height() + Dimensiones.MARGEN_PEQUENO * 2
            mensaje_x = self.ancho // 2 - mensaje_ancho // 2

            mensaje_rect = pygame.Rect(mensaje_x, mensaje_y, mensaje_ancho, mensaje_alto)
            pygame.draw.rect(superficie, (232, 245, 233), mensaje_rect, border_radius=Dimensiones.RADIO_BORDE)
            pygame.draw.rect(superficie, Colores.EXITO, mensaje_rect, width=1, border_radius=Dimensiones.RADIO_BORDE)

            # Texto del éxito
            texto_x = mensaje_x + Dimensiones.MARGEN_NORMAL
            texto_y = mensaje_y + Dimensiones.MARGEN_PEQUENO
            superficie.blit(texto_exito, (texto_x, texto_y))

    def dibujar_imagen_inferior(self, superficie):
        """Dibuja la imagen en la parte inferior con mejor posicionamiento"""
        if self.imagen:
            # Redimensionar imagen si es necesaria
            imagen_maxima = 120
            if self.imagen.get_width() > imagen_maxima or self.imagen.get_height() > imagen_maxima:
                # Mantener proporción
                ratio = min(imagen_maxima / self.imagen.get_width(),
                            imagen_maxima / self.imagen.get_height())
                nuevo_ancho = int(self.imagen.get_width() * ratio)
                nuevo_alto = int(self.imagen.get_height() * ratio)
                imagen_redimensionada = pygame.transform.scale(self.imagen, (nuevo_ancho, nuevo_alto))
            else:
                imagen_redimensionada = self.imagen

            # Posicionar en la esquina inferior derecha con margen
            pos_x = self.ancho - imagen_redimensionada.get_width() - Dimensiones.MARGEN_GRANDE
            pos_y = self.alto - imagen_redimensionada.get_height() - Dimensiones.MARGEN_GRANDE

            # Fondo sutil para la imagen
            fondo_rect = pygame.Rect(pos_x - 10, pos_y - 10,
                                     imagen_redimensionada.get_width() + 20,
                                     imagen_redimensionada.get_height() + 20)
            pygame.draw.rect(superficie, Colores.SUPERFICIE, fondo_rect, border_radius=Dimensiones.RADIO_BORDE)
            pygame.draw.rect(superficie, Colores.BORDE, fondo_rect, width=1, border_radius=Dimensiones.RADIO_BORDE)

            superficie.blit(imagen_redimensionada, (pos_x, pos_y))

    def dibujar(self, superficie):
        # Fondo principal con gradiente sutil
        superficie.fill(Colores.FONDO)

        # Dibujar elementos en orden
        self.dibujar_panel_fondo(superficie)
        self.dibujar_encabezado(superficie)

        # Componentes del formulario
        self.campo_email.dibujar(superficie)
        self.campo_password.dibujar(superficie)
        self.boton_volver.dibujar(superficie)
        self.boton_login.dibujar(superficie)

        # Mensajes y imagen
        self.dibujar_mensajes(superficie)
        self.dibujar_imagen_inferior(superficie)