# frontend/main.py
import pygame
import sys
from components.dashboard.dashboard import Dashboard
from invernadero_inteligente.frontend.config import config
from components.usuarios.login.login import Login
from components.usuarios.registro.registro_usuario import RegistroUsuario
from components.dashboard.configuracion.configuracion import Configuracion
from components.usuarios.creacion_ticket.creacion_ticket import CreacionTicket


# Configuración inicial
pygame.init()
ventana = pygame.display.set_mode(config.WINDOW_SIZE)
pygame.display.set_caption(config.APP_TITLE)


# Estados de la aplicación
ESTADOS = {
    "LOGIN": Login(*config.WINDOW_SIZE),
    "REGISTRO": RegistroUsuario(*config.WINDOW_SIZE),
    "DASHBOARD": None,  # Se inicializará después del login
    "CONFIGURACION": None,
    "CREACION_TICKET": None


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
            elif resultado == "soporte":
                ESTADOS["CREACION_TICKET"] = CreacionTicket(*config.WINDOW_SIZE, usuario_actual)
                estado_actual = "CREACION_TICKET"

            elif estado_actual == "CREACION_TICKET" and resultado == "volver_dashboard":
                estado_actual = "DASHBOARD"

            elif estado_actual == "DASHBOARD":
                if resultado == "logout":
                    usuario_actual = None
                    ESTADOS["LOGIN"].limpiar_formulario()
                    estado_actual = "LOGIN"
                elif resultado == "configuracion":
                    ESTADOS["CONFIGURACION"] = Configuracion(*config.WINDOW_SIZE, usuario_actual)
                    estado_actual = "CONFIGURACION"

            elif estado_actual == "REGISTRO" and ESTADOS["REGISTRO"].mensaje_exito:
                ESTADOS["LOGIN"].limpiar_formulario()
                estado_actual = "LOGIN"

            elif estado_actual == "CONFIGURACION" and resultado == "volver_dashboard":
                estado_actual = "DASHBOARD"



    # Dibujar
    ventana.fill(config.BACKGROUND_COLOR)
    if estado_actual in ESTADOS and ESTADOS[estado_actual]:
        # Llamar actualizar() si el objeto lo tiene
        if hasattr(ESTADOS[estado_actual], 'actualizar'):
            resultado_actualizacion = ESTADOS[estado_actual].actualizar()
            # Si actualizar() devuelve algo, podrías manejarlo aquí si es necesario

        ESTADOS[estado_actual].dibujar(ventana)


    pygame.display.flip()
    reloj.tick(60)


pygame.quit()
sys.exit()