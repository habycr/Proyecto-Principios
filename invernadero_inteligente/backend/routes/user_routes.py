# backend/routes/user_routes.py
from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService
from ..utils.logger import log

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user = AuthService.register_user(
            nombre=data['nombre'],
            email=data['email'],
            password=data['password'],
            rol=data['rol'],
            numero_serie=data['numero_serie']
        )
        log(f"Nuevo usuario registrado: {user.email}")
        return jsonify({
            "status": "success",
            "message": "Usuario registrado correctamente"
        }), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400