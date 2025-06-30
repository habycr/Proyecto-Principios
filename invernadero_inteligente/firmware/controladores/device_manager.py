# frontend/components/dashboard/esp32/device_manager.py
from .esp32_controller import ESP32Controller
from invernadero_inteligente.frontend.config import config
import time
import threading
class DeviceManager:
    """Manejador específico para controlar dispositivos del invernadero"""

    def __init__(self, esp32_controller: ESP32Controller):
        self.esp32 = esp32_controller
        self.device_mappings = {
            "bomba_agua": {
                "endpoint": "bomba",
                "acciones": {"encender": "encender", "apagar": "apagar"},
                "textos": {
                    "activar": "Activar Bomba de Agua",
                    "desactivar": "Desactivar Bomba Agua"
                }
            },
            "ventilador": {
                "endpoint": "ventilador",
                "acciones": {"encender": "encender", "apagar": "apagar"},
                "textos": {
                    "activar": "Activar Ventilador",
                    "desactivar": "Desactivar Ventilador"
                }
            },
            "uv": {
                "endpoint": "uv",
                "acciones": {"encender": "encender", "apagar": "apagar"},
                "textos": {
                    "activar": "Activar Luz Ultravioleta",
                    "desactivar": "Desactivar Luz Ultravioleta"
                }
            },
            "techo": {
                "endpoint": "motores",  # Cambiado de motorA a motores según el .ino
                "acciones": {"abrir": "adelante", "cerrar": "stop"},
                "textos": {
                    "activar": "Abrir Techo",
                    "desactivar": "Cerrar Techo"
                }
            }
        }
        self.horario_luz = {'inicio': None, 'fin': None}
        self.verificando_luz = False

    def controlar_dispositivo(self, dispositivo: str) -> dict:
        """
        Controla un dispositivo específico (enciende/apaga o abre/cierra)
        """
        if dispositivo not in self.device_mappings:
            return {
                "exito": False,
                "mensaje": f"Dispositivo {dispositivo} no encontrado",
                "nuevo_estado": False,
                "nuevo_texto": "",
                "nuevo_color": config.COLOR_BUTTON
            }

        mapping = self.device_mappings[dispositivo]
        estado_actual = self.esp32.obtener_estado_dispositivo(dispositivo)

        # Determinar acción según el estado actual
        if dispositivo == "techo":
            if estado_actual:
                # Si el techo está abierto, cerrarlo (mover hacia atrás y luego parar)
                self.esp32.enviar_comando(mapping["endpoint"], "atras")
                time.sleep(0.5)  # Esperar 500ms
                self.esp32.enviar_comando(mapping["endpoint"], "stop")
                nuevo_estado = False
            else:
                # Si el techo está cerrado, abrirlo (mover hacia adelante)
                self.esp32.enviar_comando(mapping["endpoint"], "adelante")
                nuevo_estado = True

            # Actualizar el estado del techo
            self.esp32.establecer_estado_dispositivo(dispositivo, nuevo_estado)

            # Determinar nuevo texto y color
            if nuevo_estado:
                nuevo_texto = mapping["textos"]["desactivar"]
                nuevo_color = (255, 0, 0)  # Rojo para activo
            else:
                nuevo_texto = mapping["textos"]["activar"]
                nuevo_color = config.COLOR_BUTTON  # Color normal

            return {
                "exito": True,
                "mensaje": f"Techo {'abierto' if nuevo_estado else 'cerrado'} correctamente",
                "nuevo_estado": nuevo_estado,
                "nuevo_texto": nuevo_texto,
                "nuevo_color": nuevo_color
            }
        else:
            return {
                "exito": False,
                "mensaje": f"Error al controlar {dispositivo}",
                "nuevo_estado": estado_actual,
                "nuevo_texto": mapping["textos"]["desactivar"] if estado_actual else mapping["textos"]["activar"],
                "nuevo_color": (255, 0, 0) if estado_actual else config.COLOR_BUTTON
            }

    def actualizar_datos_sensores(self) -> dict:
        """
        Actualiza y obtiene los datos de todos los sensores

        Returns:
            dict: Datos actualizados de los sensores
        """
        return self.esp32.obtener_datos_sensores()

    def obtener_datos_sensores_actuales(self) -> dict:
        """
        Obtiene los datos de sensores desde la cache (sin hacer petición HTTP)

        Returns:
            dict: Datos de sensores desde la cache
        """
        return self.esp32.obtener_datos_sensores_cache()

    def obtener_estado_dispositivo(self, dispositivo: str) -> bool:
        """Obtiene el estado actual de un dispositivo"""
        return self.esp32.obtener_estado_dispositivo(dispositivo)

    def obtener_texto_boton(self, dispositivo: str) -> str:
        """Obtiene el texto apropiado para el botón según el estado del dispositivo"""
        if dispositivo not in self.device_mappings:
            return "Dispositivo no encontrado"

        mapping = self.device_mappings[dispositivo]
        estado = self.esp32.obtener_estado_dispositivo(dispositivo)

        return mapping["textos"]["desactivar"] if estado else mapping["textos"]["activar"]

    def obtener_color_boton(self, dispositivo: str) -> tuple:
        """Obtiene el color apropiado para el botón según el estado del dispositivo"""
        estado = self.esp32.obtener_estado_dispositivo(dispositivo)
        return (255, 0, 0) if estado else config.COLOR_BUTTON

    def resetear_todos_dispositivos(self):
        """Resetea todos los dispositivos a estado apagado/cerrado"""
        for dispositivo in self.device_mappings.keys():
            if self.esp32.obtener_estado_dispositivo(dispositivo):
                self.controlar_dispositivo(dispositivo)

    def obtener_estado_sensor_critico(self) -> dict:
        """
        Verifica si algún sensor está en estado crítico

        Returns:
            dict: Estado de los sensores críticos
        """
        datos = self.obtener_datos_sensores_actuales()
        alertas = []

        # Verificar niveles críticos
        if datos.get("nivel_drenaje", 0) <= 3:
            alertas.append("⚠️ Nivel de drenaje bajo")

        if datos.get("nivel_riego", 0) <= 3:
            alertas.append("⚠️ Nivel de riego bajo")

        if datos.get("humedad_suelo", 0) <= 3:
            alertas.append("⚠️ Suelo muy seco")

        if datos.get("intensidad_luz", 0) <= 2:
            alertas.append("⚠️ Poca luz disponible")

        return {
            "hay_alertas": len(alertas) > 0,
            "alertas": alertas,
            "datos": datos
        }

    def configurar_luz_automatica(self, horario: dict):
        """Configura el horario para control automático de luz"""
        self.horario_luz = horario
        self.verificar_estado_luz()

    def verificar_estado_luz(self):
        """Verifica si la luz debe estar encendida según el horario"""
        if not self.horario_luz['inicio'] or not self.horario_luz['fin']:
            print("Horario de luz no configurado correctamente")
            return

        hora_actual = time.strftime("%H:%M:%S")
        inicio = self.horario_luz['inicio']
        fin = self.horario_luz['fin']

        print(f"Verificando luz - Hora actual: {hora_actual}, Rango: {inicio} a {fin}")

        # Si estamos dentro del horario y la luz está apagada
        if inicio <= hora_actual < fin:
            if not self.esp32.obtener_estado_dispositivo("uv"):
                print("Encendiendo luz artificial (dentro del horario)")
                self.controlar_dispositivo("uv")
        # Si estamos fuera del horario y la luz está encendida
        elif (hora_actual < inicio or hora_actual >= fin):
            if self.esp32.obtener_estado_dispositivo("uv"):
                print("Apagando luz artificial (fuera del horario)")
                self.controlar_dispositivo("uv")

    def iniciar_verificacion_periodica(self, intervalo=60):
        """Inicia un hilo para verificar periódicamente el estado de la luz"""
        if not self.verificando_luz:
            self.verificando_luz = True
            threading.Thread(
                target=self._hilo_verificacion_luz,
                args=(intervalo,),
                daemon=True
            ).start()

    def _hilo_verificacion_luz(self, intervalo):
        """Hilo que verifica periódicamente el estado de la luz"""
        while self.verificando_luz:
            self.verificar_estado_luz()
            time.sleep(intervalo)
