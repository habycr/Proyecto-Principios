# frontend/components/dashboard/esp32/esp32_controller.py
import requests
from typing import Dict, Optional
import re
import time



class ESP32Controller:
    """Controlador principal para comunicación con ESP32"""

    def __init__(self, base_url: str = "http://192.168.0.17"):
        self.base_url = base_url
        self.estados_dispositivos = {
            "bomba_agua": False,
            "ventilador": False,
            "uv": False,
            "techo": False
        }
        # Datos de sensores
        self.datos_sensores = {
            "temperatura": 0.0,
            "humedad_ambiente": 0.0,
            "nivel_drenaje": 0,
            "nivel_riego": 0,
            "intensidad_luz": 0,
            "humedad_suelo": 0,
            "ultimo_update": 0
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

    def obtener_datos_sensores(self) -> Dict:
        try:
            url = f"{self.base_url}/niveles"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                texto = response.text
                datos = {}

                def extraer_float(patron):
                    match = re.search(patron, texto)
                    return float(match.group(1)) if match else 0.0

                def extraer_int(patron):
                    match = re.search(patron, texto)
                    return int(match.group(1)) if match else 0

                datos["temperatura"] = extraer_float(r"Temperatura Ambiente:\s*([\d.]+)")
                datos["humedad_ambiente"] = extraer_float(r"Humedad Ambiente:\s*([\d.]+)")
                datos["nivel_drenaje"] = extraer_int(r"Nivel Drenaje:\s*(\d+)")
                datos["nivel_riego"] = extraer_int(r"Nivel Riego:\s*(\d+)")
                datos["intensidad_luz"] = extraer_int(r"Intensidad de Luz:\s*(\d+)")
                datos["humedad_suelo"] = extraer_int(r"Humedad del Suelo:\s*(\d+)")

                # Actualizar cache
                self.datos_sensores.update(datos)
                self.datos_sensores["ultimo_update"] = time.time()

                print(f"[DEBUG] Sensores actualizados: {datos}")
                return datos
            else:
                print(f"[ERROR] Código de respuesta: {response.status_code}")
                return {}

        except requests.exceptions.Timeout:
            print("[ERROR] Timeout al obtener datos")
        except requests.exceptions.ConnectionError:
            print("[ERROR] Conexión fallida al ESP32")
        except Exception as e:
            print(f"[ERROR] Excepción inesperada: {e}")

        return {}

    def obtener_estado_dispositivo(self, dispositivo: str) -> bool:
        """Obtiene el estado actual de un dispositivo"""
        return self.estados_dispositivos.get(dispositivo, False)

    def establecer_estado_dispositivo(self, dispositivo: str, estado: bool):
        """Establece el estado de un dispositivo"""
        self.estados_dispositivos[dispositivo] = estado

    def obtener_todos_los_estados(self) -> Dict[str, bool]:
        """Obtiene todos los estados de dispositivos"""
        return self.estados_dispositivos.copy()

    def obtener_datos_sensores_cache(self) -> Dict:
        """Obtiene los datos de sensores desde la cache"""
        return self.datos_sensores.copy()

    def cambiar_url_base(self, nueva_url: str):
        """Cambia la URL base del ESP32"""
        self.base_url = nueva_url
        print(f"URL base cambiada a: {nueva_url}")