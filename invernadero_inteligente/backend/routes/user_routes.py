# backend/routes/user_routes.py
import traceback
from flask import Blueprint, request, jsonify
from invernadero_inteligente.backend.services.auth_service import AuthService
from invernadero_inteligente.backend.utils.logger import log
from models.user import User

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