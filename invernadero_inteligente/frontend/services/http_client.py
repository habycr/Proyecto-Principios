# frontend/services/http_client.py
import requests
import json
from typing import Dict, Any, Optional


class HTTPClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout: int = 10) -> Dict[
        str, Any]:
        """
        Realiza una petición HTTP y maneja errores comunes
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")

            # Intentar parsear JSON
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {
                    "status": "error",
                    "message": f"Respuesta no válida del servidor (HTTP {response.status_code})"
                }

            # Agregar código de estado
            result["http_status"] = response.status_code
            return result

        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "No se pudo conectar al servidor. Verifique que el backend esté ejecutándose.",
                "http_status": 0
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Tiempo de espera agotado. El servidor no respondió.",
                "http_status": 0
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Error de conexión: {str(e)}",
                "http_status": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error inesperado: {str(e)}",
                "http_status": 0
            }

    def register_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Registra un nuevo usuario
        Args:
            user_data: Diccionario con los datos del usuario
        Returns:
            Dict con la respuesta del servidor
        """
        return self._make_request('POST', '/api/register', user_data)

    def login_user(self, email_or_serial: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario
        Args:
            email_or_serial: Email o número de serie
            password: Contraseña
        Returns:
            Dict con la respuesta del servidor
        """
        login_data = {
            "email_or_serial": email_or_serial,
            "password": password
        }
        return self._make_request('POST', '/api/login', login_data)

    def check_server_health(self) -> Dict[str, Any]:
        """
        Verifica el estado del servidor
        Returns:
            Dict con la respuesta del servidor
        """
        return self._make_request('GET', '/api/health')

    def test_connection(self) -> bool:
        """
        Prueba la conexión con el servidor
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        result = self.check_server_health()
        return result.get("status") == "success" and result.get("http_status") == 200