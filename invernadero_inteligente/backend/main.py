# backend/main.py
from flask import Flask
from routes.user_routes import user_bp
from config.settings import SPREADSHEET_ID

app = Flask(__name__)
app.register_blueprint(user_bp, url_prefix='/api')

if __name__ == '__main__':
    print(f"Conectado a Google Sheets ID: {SPREADSHEET_ID}")
    app.run(host='0.0.0.0', port=5000, debug=True)