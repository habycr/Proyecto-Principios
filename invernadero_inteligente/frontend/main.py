# frontend/main.py
import pygame
import sys
from components.usuarios.registro.registro_usuario import RegistroUsuario

# Configuración inicial (igual que antes)
pygame.init()
ANCHO_VENTANA = 800
ALTO_VENTANA = 800  # Aumentado para más campos
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Invernadero Inteligente - Registro de Usuario")

COLOR_FONDO = (240, 240, 240)
formulario_registro = RegistroUsuario(ANCHO_VENTANA, ALTO_VENTANA)

# Bucle principal (igual que antes)
...
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