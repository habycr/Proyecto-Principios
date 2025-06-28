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
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        if not dispositivo or not tipo_dato:
            return jsonify({
                "status": "error",
                "message": "Se requieren los parámetros 'dispositivo' y 'tipo_dato'"
            }), 400

        # Pasar los filtros de fecha al método get_by_device_and_type
        data_points = DataPoint.get_by_device_and_type(
            dispositivo,
            tipo_dato,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        if not data_points:
            mensaje_error = "No se encontraron datos para los criterios especificados"
            if fecha_inicio or fecha_fin:
                if fecha_inicio and fecha_fin:
                    mensaje_error += f" entre {fecha_inicio} y {fecha_fin}"
                elif fecha_inicio:
                    mensaje_error += f" desde {fecha_inicio}"
                elif fecha_fin:
                    mensaje_error += f" hasta {fecha_fin}"

            return jsonify({
                "status": "error",
                "message": mensaje_error
            }), 404

        chart_image = ChartService.generate_time_series_chart(dispositivo, tipo_dato, data_points)

        if not chart_image:
            raise Exception("Error generando gráfica")

        return jsonify({
            "status": "success",
            "chart": f"data:image/png;base64,{chart_image}",
            "dispositivo": dispositivo,
            "tipo_dato": tipo_dato,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_records": len(data_points)
        })

    except Exception as e:
        log(f"Error en /chart: {str(e)}", "error")
        return jsonify({
            "status": "error",
            "message": "Error al generar gráfica"
        }), 500


@data_bp.route('/raw', methods=['GET'])
def get_raw_data():
    try:
        dispositivo = request.args.get('dispositivo')
        tipo_dato = request.args.get('tipo_dato')
        limit = int(request.args.get('limit', 100))
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        incluir_estado_techo = request.args.get('incluir_estado_techo', 'false').lower() == 'true'

        if not dispositivo or not tipo_dato:
            return jsonify({
                "status": "error",
                "message": "Faltan parámetros requeridos: 'dispositivo' y 'tipo_dato'"
            }), 400

        # Pasar los filtros de fecha al método get_by_device_and_type
        data_points = DataPoint.get_by_device_and_type(
            dispositivo,
            tipo_dato,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        if not data_points:
            mensaje_error = "No se encontraron datos para los criterios especificados"
            if fecha_inicio or fecha_fin:
                if fecha_inicio and fecha_fin:
                    mensaje_error += f" entre {fecha_inicio} y {fecha_fin}"
                elif fecha_inicio:
                    mensaje_error += f" desde {fecha_inicio}"
                elif fecha_fin:
                    mensaje_error += f" hasta {fecha_fin}"

            return jsonify({
                "status": "error",
                "message": mensaje_error
            }), 404

        response_data = {
            "status": "success",
            "data": [dp.to_dict() for dp in data_points],
            "total_records": len(data_points),
            "dispositivo": dispositivo,
            "tipo_dato": tipo_dato
        }

        # Agregar información de fechas si se proporcionaron
        if fecha_inicio:
            response_data["fecha_inicio"] = fecha_inicio
        if fecha_fin:
            response_data["fecha_fin"] = fecha_fin

        return jsonify(response_data)

    except Exception as e:
        log(f"Error en /raw: {str(e)}", "error")
        return jsonify({
            "status": "error",
            "message": "Error al obtener datos"
        }), 500


@data_bp.route('/sheet', methods=['GET'])
def get_sheet_data():
    """Endpoint para obtener datos filtrados de la hoja de Google Sheets"""
    try:
        dispositivo = request.args.get('dispositivo')
        tipo_dato = request.args.get('tipo_dato')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        limit = int(request.args.get('limit', 1000))

        # Usar el método más genérico para filtrar datos
        data_points = DataPoint.get_filtered_data(
            dispositivo=dispositivo,
            tipo_dato=tipo_dato,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=limit
        )

        if not data_points:
            mensaje_error = "No se encontraron datos"
            filtros = []
            if dispositivo:
                filtros.append(f"dispositivo: {dispositivo}")
            if tipo_dato:
                filtros.append(f"tipo: {tipo_dato}")
            if fecha_inicio or fecha_fin:
                if fecha_inicio and fecha_fin:
                    filtros.append(f"fechas: {fecha_inicio} - {fecha_fin}")
                elif fecha_inicio:
                    filtros.append(f"desde: {fecha_inicio}")
                elif fecha_fin:
                    filtros.append(f"hasta: {fecha_fin}")

            if filtros:
                mensaje_error += f" para los filtros: {', '.join(filtros)}"

            return jsonify({
                "status": "error",
                "message": mensaje_error
            }), 404

        response_data = {
            "status": "success",
            "data": [dp.to_dict() for dp in data_points],
            "total_records": len(data_points)
        }

        # Agregar información de filtros aplicados
        if dispositivo:
            response_data["dispositivo"] = dispositivo
        if tipo_dato:
            response_data["tipo_dato"] = tipo_dato
        if fecha_inicio:
            response_data["fecha_inicio"] = fecha_inicio
        if fecha_fin:
            response_data["fecha_fin"] = fecha_fin

        return jsonify(response_data)

    except Exception as e:
        log(f"Error en /sheet: {str(e)}", "error")
        return jsonify({
            "status": "error",
            "message": "Error al obtener datos de la hoja"
        }), 500