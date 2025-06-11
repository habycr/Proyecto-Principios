# frontend/config.py
import os


class Config:
    # Configuración del backend
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')  # URL base del backend
    API_TIMEOUT = 5  # Tiempo de espera para las peticiones en segundos

    # Configuración de la aplicación
    APP_TITLE = "Invernadero Inteligente"
    WINDOW_SIZE = (800, 800)
    BACKGROUND_COLOR = (240, 240, 240)

    # Colores
    COLOR_SUCCESS = (0, 150, 0)
    COLOR_ERROR = (200, 0, 0)
    COLOR_BUTTON = (100, 200, 100)
    COLOR_BUTTON_SECONDARY = (200, 200, 200)


config = Config()