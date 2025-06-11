# backend/utils/logger.py
import logging
from datetime import datetime
from pathlib import Path

# Configurar el directorio de logs
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log(message: str, level: str = "INFO"):
    """
    Función de logging simplificada
    Args:
        message: Mensaje a registrar
        level: Nivel de logging (INFO, ERROR, WARNING, DEBUG)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    if level.upper() == "ERROR":
        logger.error(formatted_message)
    elif level.upper() == "WARNING":
        logger.warning(formatted_message)
    elif level.upper() == "DEBUG":
        logger.debug(formatted_message)
    else:
        logger.info(formatted_message)


def log_user_action(user_email: str, action: str):
    """Registra acciones específicas de usuario"""
    log(f"Usuario {user_email}: {action}")


def log_device_action(numero_serie: str, action: str):
    """Registra acciones específicas de dispositivo"""
    log(f"Dispositivo {numero_serie}: {action}")


def log_error(error: Exception, context: str = ""):
    """Registra errores con contexto"""
    error_msg = f"Error en {context}: {type(error).__name__}: {str(error)}"
    log(error_msg, "ERROR")