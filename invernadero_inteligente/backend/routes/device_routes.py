# backend/routes/device_routes.py
from flask import Blueprint, jsonify
from backend.models.device import Device

device_bp = Blueprint('device', __name__)


@device_bp.route('/dispositivo/<serial_number>', methods=['GET'])
def obtener_dispositivo(serial_number):
    try:
        dispositivo = Device.obtener_por_serie(serial_number)
        if not dispositivo:
            return jsonify({"status": "error", "message": "Dispositivo no encontrado"}), 404

        return jsonify({
            "status": "success",
            "dispositivo": {
                "numero_serie": dispositivo['Número de Serie'],
                "modelo": dispositivo.get('Modelo', 'N/A'),
                "estado": dispositivo.get('Estado', 'N/A'),
                "ultima_lectura": dispositivo.get('Última Lectura', 'N/A')
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
