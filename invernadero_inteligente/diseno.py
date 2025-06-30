"""
Sistema de Diseño para Invernadero Inteligente
Configuración centralizada de colores, fuentes, estilos y layouts
Basado en los requerimientos del proyecto y temática agrícola/tecnológica
"""


class Colores:
    """Paleta de colores principal del sistema"""

    # Colores principales - Inspirados en naturaleza y tecnología
    PRIMARIO = (34, 139, 34)  # Verde bosque - Principal
    PRIMARIO_HOVER = (46, 125, 50)  # Verde más claro para hover
    PRIMARIO_OSCURO = (27, 94, 32)  # Verde más oscuro para pressed

    SECUNDARIO = (76, 175, 80)  # Verde claro - Secundario
    SECUNDARIO_HOVER = (102, 187, 106)
    SECUNDARIO_OSCURO = (56, 142, 60)

    ACENTO = (255, 193, 7)  # Amarillo dorado - Sol/energía
    ACENTO_HOVER = (255, 213, 79)
    ACENTO_OSCURO = (255, 160, 0)

    # Colores de estado
    EXITO = (76, 175, 80)  # Verde - Operaciones exitosas
    ALERTA = (255, 87, 34)  # Naranja rojizo - Alertas
    ERROR = (244, 67, 54)  # Rojo - Errores críticos
    ADVERTENCIA = (255, 193, 7)  # Amarillo - Advertencias
    INFO = (33, 150, 243)  # Azul - Información

    # Colores de fondo y superficie
    FONDO = (245, 245, 245)  # Gris muy claro
    FONDO_OSCURO = (224, 224, 224)  # Gris claro
    SUPERFICIE = (255, 255, 255)  # Blanco
    SUPERFICIE_HOVER = (250, 250, 250)

    # Colores de texto
    TEXTO_PRIMARIO = (33, 33, 33)  # Gris muy oscuro
    TEXTO_SECUNDARIO = (97, 97, 97)  # Gris medio
    TEXTO_DESHABILITADO = (158, 158, 158)
    TEXTO_SOBRE_PRIMARIO = (255, 255, 255)  # Blanco sobre fondos oscuros

    # Colores específicos del sistema
    SENSOR_TEMPERATURA = (255, 87, 34)  # Naranja para temperatura
    SENSOR_HUMEDAD = (33, 150, 243)  # Azul para humedad
    SENSOR_PH = (156, 39, 176)  # Púrpura para pH
    SENSOR_LUZ = (255, 193, 7)  # Amarillo para luz

    TECHO_ABIERTO = (76, 175, 80)  # Verde para techo abierto
    TECHO_CERRADO = (158, 158, 158)  # Gris para techo cerrado

    AGUA_SUFICIENTE = (33, 150, 243)  # Azul para agua suficiente
    AGUA_BAJA = (255, 193, 7)  # Amarillo para agua baja
    AGUA_CRITICA = (244, 67, 54)  # Rojo para nivel crítico

    # Bordes y divisores
    BORDE = (224, 224, 224)
    BORDE_ACTIVO = (76, 175, 80)
    BORDE_ERROR = (244, 67, 54)
    DIVIDER = (238, 238, 238)


class Fuentes:
    """Configuración de fuentes del sistema"""

    # Familia de fuentes principal
    GENERAL = ("Segoe UI", "Arial", "sans-serif")
    MONOSPACE = ("Consolas", "Courier New", "monospace")

    # Tamaños de fuente
    TITULO_PRINCIPAL = ("Segoe UI", 32)  # Títulos principales
    TITULO = ("Segoe UI", 24)  # Títulos de sección
    SUBTITULO = ("Segoe UI", 20)  # Subtítulos
    NORMAL = ("Segoe UI", 16)  # Texto normal
    PEQUENO = ("Segoe UI", 14)  # Texto pequeño
    MINI = ("Segoe UI", 12)  # Texto muy pequeño

    # Fuentes especiales
    DATOS_SENSOR = ("Consolas", 18)  # Datos de sensores
    TIMESTAMP = ("Consolas", 12)  # Marcas de tiempo


class Dimensiones:
    """Dimensiones estándar para componentes"""

    # Botones
    BOTON_GRANDE = (200, 50)  # Botones principales
    BOTON_MEDIANO = (150, 40)  # Botones secundarios
    BOTON_PEQUENO = (100, 35)  # Botones de acción
    BOTON_ICONO = (40, 40)  # Botones solo con icono

    # Inputs
    INPUT_ANCHO = 300
    INPUT_ALTO = 40
    INPUT_PEQUENO = (200, 35)

    # Tarjetas y paneles
    TARJETA_SENSOR = (280, 150)  # Tarjetas de sensores
    PANEL_CONTROL = (320, 200)  # Paneles de control
    MODAL_PEQUENO = (400, 300)  # Modales pequeños
    MODAL_GRANDE = (600, 500)  # Modales grandes

    # Espaciado
    MARGEN_PEQUENO = 8
    MARGEN_NORMAL = 16
    MARGEN_GRANDE = 24
    MARGEN_EXTRA = 32

    # Bordes y radios
    RADIO_BORDE = 8
    RADIO_TARJETA = 12
    GROSOR_BORDE = 2


class EstiloBoton:
    """Estilos predefinidos para botones"""

    PRIMARIO = {
        "bg": Colores.PRIMARIO,
        "bg_hover": Colores.PRIMARIO_HOVER,
        "bg_pressed": Colores.PRIMARIO_OSCURO,
        "fg": Colores.TEXTO_SOBRE_PRIMARIO,
        "borde": Colores.PRIMARIO,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    SECUNDARIO = {
        "bg": Colores.SECUNDARIO,
        "bg_hover": Colores.SECUNDARIO_HOVER,
        "bg_pressed": Colores.SECUNDARIO_OSCURO,
        "fg": Colores.TEXTO_SOBRE_PRIMARIO,
        "borde": Colores.SECUNDARIO,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    ACENTO = {
        "bg": Colores.ACENTO,
        "bg_hover": Colores.ACENTO_HOVER,
        "bg_pressed": Colores.ACENTO_OSCURO,
        "fg": Colores.TEXTO_PRIMARIO,
        "borde": Colores.ACENTO,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    SUPERFICIE = {
        "bg": Colores.SUPERFICIE,
        "bg_hover": Colores.SUPERFICIE_HOVER,
        "bg_pressed": Colores.FONDO_OSCURO,
        "fg": Colores.TEXTO_PRIMARIO,
        "borde": Colores.BORDE,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    PELIGRO = {
        "bg": Colores.ERROR,
        "bg_hover": (211, 47, 47),
        "bg_pressed": (183, 28, 28),
        "fg": Colores.TEXTO_SOBRE_PRIMARIO,
        "borde": Colores.ERROR,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    # Botones específicos del sistema
    RIEGO = {
        "bg": Colores.AGUA_SUFICIENTE,
        "bg_hover": (30, 136, 229),
        "bg_pressed": (25, 118, 210),
        "fg": Colores.TEXTO_SOBRE_PRIMARIO,
        "borde": Colores.AGUA_SUFICIENTE,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }

    LUZ = {
        "bg": Colores.SENSOR_LUZ,
        "bg_hover": Colores.ACENTO_HOVER,
        "bg_pressed": Colores.ACENTO_OSCURO,
        "fg": Colores.TEXTO_PRIMARIO,
        "borde": Colores.SENSOR_LUZ,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }


class EstiloInput:
    """Estilos para campos de entrada"""

    NORMAL = {
        "bg": Colores.SUPERFICIE,
        "bg_focus": Colores.SUPERFICIE,
        "fg": Colores.TEXTO_PRIMARIO,
        "placeholder": Colores.TEXTO_SECUNDARIO,
        "borde": Colores.BORDE,
        "borde_focus": Colores.BORDE_ACTIVO,
        "borde_error": Colores.BORDE_ERROR,
        "fuente": Fuentes.NORMAL,
        "radio": Dimensiones.RADIO_BORDE
    }


class EstiloLabel:
    """Estilos para etiquetas y texto"""

    TITULO = {
        "fg": Colores.TEXTO_PRIMARIO,
        "fuente": Fuentes.TITULO
    }

    SUBTITULO = {
        "fg": Colores.TEXTO_PRIMARIO,
        "fuente": Fuentes.SUBTITULO
    }

    NORMAL = {
        "fg": Colores.TEXTO_PRIMARIO,
        "fuente": Fuentes.NORMAL
    }

    SECUNDARIO = {
        "fg": Colores.TEXTO_SECUNDARIO,
        "fuente": Fuentes.NORMAL
    }

    PEQUENO = {
        "fg": Colores.TEXTO_SECUNDARIO,
        "fuente": Fuentes.PEQUENO
    }

    SENSOR = {
        "fg": Colores.TEXTO_PRIMARIO,
        "fuente": Fuentes.DATOS_SENSOR
    }

    TIMESTAMP = {
        "fg": Colores.TEXTO_SECUNDARIO,
        "fuente": Fuentes.TIMESTAMP
    }


class EstiloTarjeta:
    """Estilos para tarjetas y paneles"""

    SENSOR = {
        "bg": Colores.SUPERFICIE,
        "borde": Colores.BORDE,
        "radio": Dimensiones.RADIO_TARJETA,
        "sombra": True,
        "padding": Dimensiones.MARGEN_NORMAL
    }

    CONTROL = {
        "bg": Colores.SUPERFICIE,
        "borde": Colores.BORDE,
        "radio": Dimensiones.RADIO_TARJETA,
        "sombra": True,
        "padding": Dimensiones.MARGEN_GRANDE
    }

    ALERTA = {
        "bg": (255, 245, 238),  # Fondo naranja muy claro
        "borde": Colores.ALERTA,
        "radio": Dimensiones.RADIO_BORDE,
        "sombra": False,
        "padding": Dimensiones.MARGEN_NORMAL
    }


class Layouts:
    """Configuraciones de layout y posicionamiento"""

    # Grids y distribución
    GRID_SENSORES = {
        "columnas": 3,
        "filas": 2,
        "espacio_h": Dimensiones.MARGEN_NORMAL,
        "espacio_v": Dimensiones.MARGEN_NORMAL
    }

    GRID_CONTROLES = {
        "columnas": 2,
        "filas": 3,
        "espacio_h": Dimensiones.MARGEN_GRANDE,
        "espacio_v": Dimensiones.MARGEN_GRANDE
    }

    # Posiciones estándar
    CENTRADO_HORIZONTAL = "center_x"
    CENTRADO_VERTICAL = "center_y"
    CENTRADO_COMPLETO = "center"

    # Barras de navegación
    NAVBAR_ALTURA = 60
    SIDEBAR_ANCHO = 250

    # Contenido principal
    CONTENIDO_PADDING = Dimensiones.MARGEN_GRANDE
    SECCION_SPACING = Dimensiones.MARGEN_EXTRA


class Iconos:
    """Configuración de iconos del sistema"""

    # Sensores
    TEMPERATURA = "🌡️"
    HUMEDAD = "💧"
    PH = "⚗️"
    LUZ = "☀️"

    # Controles
    RIEGO = "🚿"
    VENTILADOR = "🌀"
    TECHO = "🏠"
    LUZ_ARTIFICIAL = "💡"

    # Estados
    ACTIVO = "🟢"
    INACTIVO = "🔴"
    ADVERTENCIA = "⚠️"
    INFO = "ℹ️"

    # Navegación
    CONFIGURACION = "⚙️"
    GRAFICO = "📊"
    CAMARA = "📷"
    TICKET = "🎫"
    USUARIO = "👤"
    SALIR = "🚪"


class Animaciones:
    """Configuración de animaciones y transiciones"""

    # Duraciones (en milisegundos)
    RAPIDA = 150
    NORMAL = 250
    LENTA = 350

    # Tipos de easing
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"

    # Efectos
    FADE_IN = {"tipo": "fade", "duracion": NORMAL}
    SLIDE_UP = {"tipo": "slide", "direccion": "up", "duracion": NORMAL}
    SLIDE_DOWN = {"tipo": "slide", "direccion": "down", "duracion": NORMAL}


class Responsive:
    """Configuraciones responsive para diferentes tamaños de pantalla"""

    # Breakpoints
    MOBILE = 480
    TABLET = 768
    DESKTOP = 1024
    LARGE = 1440

    # Configuraciones por dispositivo
    MOBILE_CONFIG = {
        "grid_columnas": 1,
        "sidebar_ancho": 200,
        "padding": Dimensiones.MARGEN_PEQUENO
    }

    TABLET_CONFIG = {
        "grid_columnas": 2,
        "sidebar_ancho": 220,
        "padding": Dimensiones.MARGEN_NORMAL
    }

    DESKTOP_CONFIG = {
        "grid_columnas": 3,
        "sidebar_ancho": 250,
        "padding": Dimensiones.MARGEN_GRANDE
    }


class Temas:
    """Configuración de temas alternativos"""

    # Tema nocturno (opcional para futuras versiones)
    NOCTURNO = {
        "fondo": (18, 18, 18),
        "superficie": (33, 33, 33),
        "texto_primario": (255, 255, 255),
        "texto_secundario": (158, 158, 158),
        "primario": (102, 187, 106),  # Verde más claro para contraste
        "acento": (255, 213, 79)
    }


# Funciones de utilidad para el sistema de diseño

def obtener_color_sensor(tipo_sensor):
    """Obtiene el color asociado a un tipo de sensor"""
    colores = {
        "temperatura": Colores.SENSOR_TEMPERATURA,
        "humedad": Colores.SENSOR_HUMEDAD,
        "ph": Colores.SENSOR_PH,
        "luz": Colores.SENSOR_LUZ
    }
    return colores.get(tipo_sensor.lower(), Colores.TEXTO_PRIMARIO)


def obtener_icono_sensor(tipo_sensor):
    """Obtiene el icono asociado a un tipo de sensor"""
    iconos = {
        "temperatura": Iconos.TEMPERATURA,
        "humedad": Iconos.HUMEDAD,
        "ph": Iconos.PH,
        "luz": Iconos.LUZ
    }
    return iconos.get(tipo_sensor.lower(), "📊")


def calcular_posicion_centrada(contenedor_ancho, contenedor_alto, elemento_ancho, elemento_alto):
    """Calcula la posición para centrar un elemento dentro de un contenedor"""
    x = (contenedor_ancho - elemento_ancho) // 2
    y = (contenedor_alto - elemento_alto) // 2
    return (x, y)


def calcular_grid_posicion(indice, columnas, ancho_elemento, alto_elemento, espacio_h, espacio_v, margen_x=0,
                           margen_y=0):
    """Calcula la posición de un elemento en un grid"""
    fila = indice // columnas
    columna = indice % columnas

    x = margen_x + columna * (ancho_elemento + espacio_h)
    y = margen_y + fila * (alto_elemento + espacio_v)

    return (x, y)


def obtener_estilo_por_estado(estado, tipo="boton"):
    """Obtiene el estilo apropiado basado en el estado del sistema"""
    if tipo == "boton":
        if estado == "activo":
            return EstiloBoton.PRIMARIO
        elif estado == "inactivo":
            return EstiloBoton.SUPERFICIE
        elif estado == "alerta":
            return EstiloBoton.PELIGRO
        elif estado == "procesando":
            return EstiloBoton.ACENTO

    return EstiloBoton.SUPERFICIE


def validar_accesibilidad_color(color_fondo, color_texto):
    """Valida si la combinación de colores cumple con estándares de accesibilidad"""
    # Función simplificada - en implementación real calcularía el contraste
    # Por ahora solo verifica que no sean el mismo color
    return color_fondo != color_texto


# Configuración global del sistema de diseño
SISTEMA_DISENO = {
    "version": "1.0.0",
    "nombre": "Invernadero Inteligente Design System",
    "descripcion": "Sistema de diseño completo para la aplicación de invernadero inteligente",
    "tema_activo": "claro",
    "responsive": True,
    "animaciones": True
}