import pygame
import time
from pathlib import Path
from invernadero_inteligente.frontend.components.usuarios.registro.elementos.boton import Boton
from invernadero_inteligente.frontend.config import config

class Timelapse:
    def __init__(self, ancho_ventana, alto_ventana, usuario):
        self.ancho_ventana = ancho_ventana
        self.alto_ventana = alto_ventana
        self.usuario = usuario
        self.usuario = usuario
        self.fuente_titulo = pygame.font.Font(None, 36)
        self.fuente_normal = pygame.font.Font(None, 28)
        self.crear_componentes()

    def crear_componentes(self):
        self.boton_cerrar = Boton(
            x=self.ancho - 170,
            y=20,
            ancho = 150,
            texto = "VOLVER",
            color=config.COLOR_BUTTON_SECONDARY
        )
# Carpeta donde se encuentran las imágenes JPEG del timelapse
IMAGE_DIR = Path("timelapse_images")

# Inicializamos todos los módulos de Pygame
pygame.init()

screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

def load_images():
    """
    Retorna una lista ordenada de todas las imágenes JPEG en la carpeta.
    Se ordenan por nombre (útil si usas timestamps en el nombre).
    """
    return sorted(IMAGE_DIR.glob("*.jpg"))

# Bucle principal del timelapse
while True:
    # Recorremos todas las imágenes encontradas
    for image_path in load_images():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Cargamos la imagen desde el disco
        img = pygame.image.load(str(image_path))

        # Redimensionamos la imagen al tamaño de la ventana (320x240)
        img = pygame.transform.scale(img, (320, 240))

        # Dibujamos la imagen en pantalla
        screen.blit(img, (0, 0))

        # Actualizamos la pantalla para que la imagen se vea
        pygame.display.flip()

        # Esperamos 0.3 segundos entre imagen e imagen (ajusta para más o menos velocidad)
        time.sleep(0.3)

    # Esperamos 1 segundo antes de volver a empezar (en caso de que no haya nuevas imágenes)
    time.sleep(1)
