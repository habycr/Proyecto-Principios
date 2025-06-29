# backend/main.py
from flask import Flask
from flask_cors import CORS
from invernadero_inteligente.backend.routes.user_routes import user_bp
from invernadero_inteligente.backend.routes.ticket_routes import ticket_bp
from invernadero_inteligente.backend.config.settings import SPREADSHEET_ID, DEBUG_MODE, SERVER_HOST, SERVER_PORT
from routes.data_router import data_bp
from invernadero_inteligente.backend.routes.device_routes import device_bp


# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS para permitir peticiones desde el frontend
CORS(app, origins=["*"])  # En producción, especifica dominios específicos

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(ticket_bp, url_prefix='/api')
# Ruta raíz para verificar que el servidor funciona
app.register_blueprint(device_bp, url_prefix='/api')
@app.route('/')
def home():
    return {
        "message": "Backend del Invernadero Inteligente",
        "status": "funcionando",
        "google_sheets_id": SPREADSHEET_ID
    }


if __name__ == '__main__':
    print("=" * 50)
    print("🌱 INVERNADERO INTELIGENTE - BACKEND")
    print("=" * 50)
    print(f"📊 Google Sheets ID: {SPREADSHEET_ID}")
    print(f"🌐 Servidor: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"🔧 Debug Mode: {DEBUG_MODE}")
    print("=" * 50)
    print("Endpoints disponibles:")
    print("  POST /api/register  - Registrar usuario")
    print("  POST /api/login     - Autenticar usuario")
    print("  GET  /api/health    - Estado del servidor")
    print("=" * 50)

    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)