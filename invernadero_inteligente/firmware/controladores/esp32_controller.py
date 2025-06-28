# frontend/components/dashboard/esp32/esp32_controller.py
import requests
from typing import Dict, Optional


class ESP32Controller:
    """Controlador principal para comunicación con ESP32"""

    def __init__(self, base_url: str = "http://172.19.14.137"):
        self.base_url = base_url
        self.estados_dispositivos = {
            "bomba_agua": False,
            "ventilador": False,
            "uv": False,
            "techo": False
        }

    def enviar_comando(self, dispositivo: str, accion: str) -> bool:
        """
        Envía un comando al ESP32

        Args:
            dispositivo: Nombre del dispositivo/endpoint
            accion: Acción a realizar (encender, apagar, adelante, stop, etc.)

        Returns:
            bool: True si el comando se envió correctamente, False en caso contrario
        """
        try:
            url = f"{self.base_url}/{dispositivo}/{accion}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                print(f"Comando {accion} para {dispositivo} enviado correctamente")
                return True
            else:
                print(f"Error al enviar comando: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            print(f"Timeout al enviar comando a {dispositivo}")
            return False
        except requests.exceptions.ConnectionError:
            print(f"Error de conexión con ESP32: {dispositivo}")
            return False
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return False

    def obtener_estado_dispositivo(self, dispositivo: str) -> bool:
        """Obtiene el estado actual de un dispositivo"""
        return self.estados_dispositivos.get(dispositivo, False)

    def establecer_estado_dispositivo(self, dispositivo: str, estado: bool):
        """Establece el estado de un dispositivo"""
        self.estados_dispositivos[dispositivo] = estado

    def obtener_todos_los_estados(self) -> Dict[str, bool]:
        """Obtiene todos los estados de dispositivos"""
        return self.estados_dispositivos.copy()

    def cambiar_url_base(self, nueva_url: str):
        """Cambia la URL base del ESP32"""
        self.base_url = nueva_url
        print(f"URL base cambiada a: {nueva_url}")