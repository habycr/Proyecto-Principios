from flask import Blueprint, request, jsonify
from models.data import DataPoint
from invernadero_inteligente.backend.utils.logger import log
from datetime import datetime, timedelta
from services.chart_service import ChartService

data_bp = Blueprint('data', __name__)


@data_bp.route('/chart', methods=['GET'])
def get_chart():
    try:
        dispositivo = request.args.get('dispositivo')
        tipo_dato = request.args.get('tipo_dato')
        limit = int(request.args.get('limit', 100))

        if not dispositivo or not tipo_dato:
            return jsonify({
                "status": "error",
                "message": "Se requieren los parámetros 'dispositivo' y 'tipo_dato'"
            }), 400

        data_points = DataPoint.get_by_device_and_type(dispositivo, tipo_dato, limit)

        if not data_points:
            return jsonify({
                "status": "error",
                "message": "No se encontraron datos para los criterios especificados"
            }), 404

        chart_image = ChartService.generate_time_series_chart(dispositivo, tipo_dato, data_points)

        if not chart_image:
            raise Exception("Error generando gráfica")

        return jsonify({
            "status": "success",
            "chart": f"data:image/png;base64,{chart_image}",
            "dispositivo": dispositivo,
            "tipo_dato": tipo_dato
        })

    except Exception as e:
        log(f"Error en /chart: {str(e)}", "error")
        return jsonify({
            "status": "error",
            "message": "Error al generar gráfica"
        }), 500