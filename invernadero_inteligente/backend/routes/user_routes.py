# backend/routes/user_routes.py
import traceback
from flask import Blueprint, request, jsonify
from invernadero_inteligente.backend.services.auth_service import AuthService
from invernadero_inteligente.backend.utils.logger import log
from models.device import Device
from models.user import User
from services.google_sheets import GoogleSheetsDB

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Datos recibidos:", data)  # Debug

    try:
        result = AuthService.register_user(data)
        return jsonify({
            "status": "success",
            "message": "Usuario registrado exitosamente",
            "user": result
        }), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        print(f"Error interno: {str(e)}")  # Debug
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    print("Datos recibidos:", request.json)  # Debug
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                "status": "error",
                "message": "Datos incompletos"
            }), 400

        print("Buscando usuario:", data['email'])  # Debug
        user = User.find_by_email(data['email'])
        print("Usuario encontrado:", user)  # Debug
        result = AuthService.login_user(data['email'], data['password'])
        return jsonify(result)

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 401
    except Exception as e:
        print(f"ERROR INTERNO: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}",
            "debug": traceback.format_exc()  # Solo para desarrollo
        }), 500

@user_bp.route('/agregar_dispositivo', methods=['POST'])
def agregar_dispositivo():
    try:
        data = request.get_json()
        email = data.get('email')
        nuevo_serial = data.get('serial')

        if not email or not nuevo_serial:
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400

        if not Device.exists(nuevo_serial):
            return jsonify({"status": "error", "message": "El dispositivo no existe"}), 404

        if not Device.is_available(nuevo_serial):
            return jsonify({"status": "error", "message": "El dispositivo ya está asignado"}), 400

        if User.device_assigned_to_other_user(nuevo_serial, email):
            return jsonify({"status": "error", "message": "El dispositivo ya pertenece a otro usuario"}), 403

        # Asociar en la hoja de Dispositivos
        Device.associate_to_user(nuevo_serial, email)

        # Actualizar en la hoja de Usuarios
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Usuarios")
        all_values = worksheet.get_all_values()  # Incluye encabezados

        for row_idx, row in enumerate(all_values[1:], start=2):  # Saltar encabezado
            email_cell = row[1].strip().lower() if len(row) > 1 else ""
            if email_cell == email.strip().lower():
                actuales = row[4] if len(row) > 4 else ""
                seriales = [s.strip() for s in actuales.split(',') if s.strip()]
                if nuevo_serial not in seriales:
                    seriales.append(nuevo_serial)
                nuevos_seriales = ', '.join(seriales)
                worksheet.update_cell(row_idx, 5, nuevos_seriales)  # Columna 5 = numero_serie
                break

        return jsonify({"status": "success", "message": "Dispositivo agregado correctamente"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/usuario/<email>', methods=['PUT'])
def actualizar_usuario(email):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "Datos no proporcionados"}), 400

        registro_actual = User.find_by_email(email)
        if not registro_actual:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Usuarios")
        all_values = worksheet.get_all_values()
        headers = all_values[0]

        for idx, row in enumerate(all_values[1:], start=2):
            if row[1].strip().lower() == email.strip().lower():
                nuevo_nombre = data.get("nombre", row[0])
                nuevo_email = data.get("email", row[1])
                nueva_ubicacion = data.get("ubicacion", row[5])

                worksheet.update_cell(idx, headers.index("Nombre") + 1, nuevo_nombre)
                worksheet.update_cell(idx, headers.index("Email") + 1, nuevo_email)
                worksheet.update_cell(idx, headers.index("Ubicación") + 1, nueva_ubicacion)

                return jsonify({
                    "status": "success",
                    "message": "Perfil actualizado correctamente"
                })

        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al actualizar perfil: {str(e)}"}), 500

@user_bp.route('/usuario/<email>', methods=['GET'])
def obtener_usuario(email):
    try:
        usuario = User.find_by_email(email)
        if not usuario:
            return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

        return jsonify({
            "status": "success",
            "usuario": usuario
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener usuario: {str(e)}"}), 500

