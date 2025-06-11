# frontend/main.py
import pygame
import sys
from components.dashboard.dashboard import Dashboard
from invernadero_inteligente.frontend.config import config
from components.usuarios.login.login_admin import Login
from components.usuarios.registro.registro_usuario import RegistroUsuario


# Configuración inicial
pygame.init()
ventana = pygame.display.set_mode(config.WINDOW_SIZE)
pygame.display.set_caption(config.APP_TITLE)


# Estados de la aplicación
ESTADOS = {
    "LOGIN": Login(*config.WINDOW_SIZE),
    "REGISTRO": RegistroUsuario(*config.WINDOW_SIZE),
    "DASHBOARD": None  # Se inicializará después del login
}


estado_actual = "LOGIN"
usuario_actual = None


# Bucle principal
reloj = pygame.time.Clock()
ejecutando = True


while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if estado_actual in ESTADOS and ESTADOS[estado_actual]:
            resultado = ESTADOS[estado_actual].manejar_evento(evento)

            # Manejar transiciones de estado
            if estado_actual == "LOGIN" and ESTADOS["LOGIN"].usuario_autenticado:
                usuario_actual = ESTADOS["LOGIN"].usuario_autenticado
                ESTADOS["DASHBOARD"] = Dashboard(*config.WINDOW_SIZE, usuario_actual)
                estado_actual = "DASHBOARD"

            elif estado_actual == "DASHBOARD" and resultado == "logout":
                usuario_actual = None
                ESTADOS["LOGIN"].limpiar_formulario()
                estado_actual = "LOGIN"

            elif estado_actual == "REGISTRO" and ESTADOS["REGISTRO"].mensaje_exito:
                ESTADOS["LOGIN"].limpiar_formulario()
                estado_actual = "LOGIN"

    # Dibujar
    ventana.fill(config.BACKGROUND_COLOR)

    if estado_actual in ESTADOS and ESTADOS[estado_actual]:
        ESTADOS[estado_actual].dibujar(ventana)

    pygame.display.flip()
    reloj.tick(60)


pygame.quit()
sys.exit()