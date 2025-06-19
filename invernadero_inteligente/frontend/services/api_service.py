# frontend/services/api_service.py
import requests
import os
import sys
import pygame
import io
import base64
from datetime import datetime

# Añadir el directorio frontend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..config import config


class APIService:
    @staticmethod
    @staticmethod
    def _make_request(endpoint, data=None, method='POST', params=None):
        try:
            url = f"{config.BACKEND_URL}/api{endpoint}"
            headers = {'Content-Type': 'application/json'}

            if method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=config.API_TIMEOUT)
            elif method == 'GET':
                response = requests.get(url, params=params, timeout=config.API_TIMEOUT)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=config.API_TIMEOUT)
            else:
                return {"status": "error", "message": f"Método HTTP no soportado: {method}"}

            if not response.ok:
                return {
                    "status": "error",
                    "message": f"Error del servidor: {response.status_code}"
                }
            return response.json()
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "El servidor está tardando más de lo esperado"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Error de conexión: {str(e)}"}

    # Métodos de autenticación
    @staticmethod
    def registrar_usuario(data):
        return APIService._make_request('/register', data)

    @staticmethod
    def iniciar_sesion(credenciales):
        return APIService._make_request('/login', credenciales)

    # Métodos de dispositivos
    @staticmethod
    def obtener_dispositivo(numero_serie):
        return APIService._make_request(f'/dispositivo/{numero_serie}', method='GET')

    # Métodos de datos
    @staticmethod
    def obtener_datos_historicos(dispositivo, tipo_dato, limit=100):
        params = {
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato,
            'limit': limit
        }
        return APIService._make_request('/data/historical', method='GET', params=params)

    @staticmethod
    def obtener_grafica(dispositivo, tipo_dato, limit=100):
        params = {
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato,
            'limit': limit
        }
        response = APIService._make_request('/data/chart', method='GET', params=params)

        if response.get('status') != 'success':
            return APIService._crear_superficie_error(response.get('message', 'Error al cargar gráfica'))

        try:
            return APIService._base64_a_surface(response['chart'])
        except Exception as e:
            print(f"Error procesando gráfica: {e}")
            return APIService._crear_superficie_error("Formato de gráfica inválido")

    @staticmethod
    def verificar_estado_servidor():
        try:
            response = requests.get(
                f"{config.BACKEND_URL}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # Métodos auxiliares privados
    @staticmethod
    def _base64_a_surface(chart_data):
        """Convierte base64 a superficie Pygame"""
        image_data = base64.b64decode(chart_data.split(',')[1])
        image_file = io.BytesIO(image_data)
        return pygame.image.load(image_file).convert_alpha()

    @staticmethod
    def _crear_superficie_error(mensaje):
        """Crea una superficie de error para mostrar en Pygame"""
        surface = pygame.Surface((800, 400))
        surface.fill(config.COLOR_ERROR)
        font = pygame.font.SysFont(None, 24)
        text = font.render(mensaje, True, (255, 255, 255))
        surface.blit(text, (50, 50))
        return surface

    @staticmethod
    def agregar_dispositivo(email, serial):
        return APIService._make_request('/agregar_dispositivo', {
            "email": email,
            "serial": serial
        }, method='POST')

    @staticmethod
    def actualizar_perfil(email, datos_actualizados):
        return APIService._make_request(f"/usuario/{email}", datos_actualizados, method='PUT')
    @staticmethod
    def obtener_usuario(email):
        """Obtiene la información de un usuario por su email"""
        return APIService._make_request(f"/usuario/{email}", method='GET')
