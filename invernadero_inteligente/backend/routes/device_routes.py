# backend/routes/device_routes.py
from flask import Blueprint, jsonify, request
from backend.models.device import Device

device_bp = Blueprint('device', __name__)


@device_bp.route('/dispositivo/<serial_number>', methods=['GET'])
def obtener_dispositivo(serial_number):
    try:
        dispositivo = Device.obtener_por_serie(serial_number)
        if not dispositivo:
            return jsonify({"status": "error", "message": "Dispositivo no encontrado"}), 404

        # Parsear las alertas existentes para incluirlas en la respuesta
        alertas_config = Device.obtener_alertas(serial_number)

        return jsonify({
            "status": "success",
            "dispositivo": {
                "numero_serie": dispositivo['Número de Serie'],
                "modelo": dispositivo.get('Modelo', 'N/A'),
                "estado": dispositivo.get('Estado', 'N/A'),
                "ultima_lectura": dispositivo.get('Última Lectura', 'N/A'),
                "Alerta_Temperatura": alertas_config.get('temperatura', {}) if alertas_config else {},
                "Alerta_Humedad_Suelo": alertas_config.get('humedad_suelo', {}) if alertas_config else {},
                "Alerta_Humedad_Ambiente": alertas_config.get('humedad_ambiente', {}) if alertas_config else {},
                "Alerta_Nivel_Agua_Drenaje": alertas_config.get('nivel_drenaje', '') if alertas_config else '',
                "Alerta_Nivel_Agua_Bomba": alertas_config.get('nivel_bomba', '') if alertas_config else ''
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@device_bp.route('/dispositivo/alertas', methods=['POST'])
def guardar_alertas_dispositivo():
    """Guarda la configuración de alertas de un dispositivo en Google Sheets"""
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data or 'numero_serie' not in data or 'alertas' not in data:
            return jsonify({
                "status": "error",
                "message": "Faltan datos requeridos: numero_serie y alertas"
            }), 400

        numero_serie = data['numero_serie']
        alertas_config = data['alertas']

        # Verificar que el dispositivo existe
        if not Device.exists(numero_serie):
            return jsonify({
                "status": "error",
                "message": f"Dispositivo {numero_serie} no encontrado"
            }), 404

        # Actualizar las alertas en Google Sheets
        Device.actualizar_alertas(numero_serie, data)

        return jsonify({
            "status": "success",
            "message": "Configuración de alertas guardada exitosamente",
            "numero_serie": numero_serie
        })

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        print(f"Error guardando alertas: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


@device_bp.route('/dispositivo/<serial_number>/alertas', methods=['GET'])
def obtener_alertas_dispositivo(serial_number):
    """Obtiene la configuración de alertas de un dispositivo desde Google Sheets"""
    try:
        # Verificar que el dispositivo existe
        if not Device.exists(serial_number):
            return jsonify({
                "status": "error",
                "message": f"Dispositivo {serial_number} no encontrado"
            }), 404

        # Obtener las alertas del dispositivo
        alertas_config = Device.obtener_alertas(serial_number)

        if alertas_config is None:
            return jsonify({
                "status": "error",
                "message": "No se pudo obtener la configuración de alertas"
            }), 500

        return jsonify({
            "status": "success",
            "numero_serie": serial_number,
            "alertas": alertas_config
        })

    except Exception as e:
        print(f"Error obteniendo alertas: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500