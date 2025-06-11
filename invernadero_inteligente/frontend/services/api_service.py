# frontend/services/api_service.py
import requests
import os
import sys
# Añadir el directorio frontend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..config import config

class APIService:
    @staticmethod
    def _make_request(endpoint, data):
        try:
            response = requests.post(
                f"{config.BACKEND_URL}/api{endpoint}",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
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

    @staticmethod
    def registrar_usuario(data):
        return APIService._make_request('/register', data)

    @staticmethod
    def iniciar_sesion(credenciales):
        return APIService._make_request('/login', credenciales)

    @staticmethod
    def obtener_dispositivo(numero_serie):
        try:
            response = requests.get(
                f"{config.BACKEND_URL}/api/dispositivo/{numero_serie}",
                timeout=config.API_TIMEOUT
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}