# frontend/main.py
import pygame
import sys
from components.dispositivos.registro.registro_dispositivo import RegistroDispositivo

# Inicialización de pygame
pygame.init()

# Configuración de la ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Invernadero Inteligente - Registro de Dispositivo")

# Color de fondo
COLOR_FONDO = (240, 240, 240)

# Crear instancia del formulario de registro
formulario_registro = RegistroDispositivo(ANCHO_VENTANA, ALTO_VENTANA)

# Bucle principal
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        # Pasar eventos al formulario
        formulario_registro.manejar_evento(evento)

    # Actualizar
    ventana.fill(COLOR_FONDO)

    # Dibujar formulario
    formulario_registro.dibujar(ventana)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()