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
    def _make_request(endpoint, data=None, method='POST', params=None):
        try:
            url = f"{config.BACKEND_URL}/api{endpoint}"
            headers = {'Content-Type': 'application/json'}

            # Limpiar parámetros None para evitar enviar valores vacíos
            if params:
                params = {k: v for k, v in params.items() if v is not None and v != ''}

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

    @staticmethod
    def obtener_dispositivo(numero_serie):
        return APIService._make_request(f'/dispositivo/{numero_serie}', method='GET')

    # Métodos de datos
    @staticmethod
    def obtener_datos_historicos(dispositivo, tipo_dato, limit=100, fecha_inicio=None, fecha_fin=None):
        params = {
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato,
            'limit': limit
        }

        # Agregar filtros de fecha si se proporcionan
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin

        return APIService._make_request('/data/historical', method='GET', params=params)

    @staticmethod
    def obtener_grafica(dispositivo, tipo_dato, limit=100, fecha_inicio=None, fecha_fin=None):
        params = {
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato,
            'limit': limit
        }

        # Agregar filtros de fecha si se proporcionan
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin

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

    @staticmethod
    def crear_ticket(data):
        return APIService._make_request('/ticket', data, method='POST')

    @staticmethod
    def obtener_datos_hoja(dispositivo=None, tipo_dato=None, fecha_inicio=None, fecha_fin=None, limit=1000):
        """Obtiene datos de la hoja 'Datos' de Google Sheets"""
        params = {
            'limit': limit
        }

        if dispositivo:
            params['dispositivo'] = dispositivo
        if tipo_dato:
            params['tipo_dato'] = tipo_dato
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
        if fecha_fin:
            params['fecha_fin'] = fecha_fin

        return APIService._make_request('/data/sheet', method='GET', params=params)

    @staticmethod
    def obtener_datos_raw(dispositivo, tipo_dato, limit=100, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos crudos incluyendo EstadoTecho con filtro opcional de fechas

        Args:
            dispositivo: Número de serie del dispositivo
            tipo_dato: Tipo de sensor
            limit: Límite de registros
            fecha_inicio: Fecha de inicio en formato "DD/MM/YYYY" (opcional)
            fecha_fin: Fecha de fin en formato "DD/MM/YYYY" (opcional)
        """
        params = {
            'dispositivo': dispositivo,
            'tipo_dato': tipo_dato,
            'limit': limit,
            'incluir_estado_techo': 'true'
        }

        # Agregar filtros de fecha si se proporcionan
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            print(f"APIService: Enviando fecha_inicio = {fecha_inicio}")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            print(f"APIService: Enviando fecha_fin = {fecha_fin}")

        print(f"APIService: Parámetros enviados = {params}")

        response = APIService._make_request('/data/raw', method='GET', params=params)

        print(f"APIService: Respuesta recibida = {response.get('status')}")
        if response.get('status') == 'success':
            print(f"APIService: Total registros recibidos = {len(response.get('data', []))}")

        # Asegurarse de que los datos tengan EstadoTecho
        if response.get("status") == "success" and "data" in response:
            for item in response["data"]:
                if "estado_techo" not in item:
                    item["estado_techo"] = 0  # Valor por defecto si no está presente

        return response