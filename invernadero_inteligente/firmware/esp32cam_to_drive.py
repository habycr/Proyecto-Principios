import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
from pathlib import Path

ESP32_CAM_IP = "http://192.168.0.27"
CAPTURE_URL = f"{ESP32_CAM_IP}/capture"
CREDENTIAL_PATH = Path(__file__).parent/"credentials.json"
SECRET_PATH = Path(__file__).parent/"client_secrets.json"

def take_photo_and_upload():
    #Capturar imagen
    response = requests.get(CAPTURE_URL)
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Imagen guardada: {filename}")
    else:
        print(f"Error: {response.status_code}")
        exit()

#Subir a Google Drive
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(str(SECRET_PATH))
    if CREDENTIAL_PATH.exists():
        gauth.LoadCredentialsFile(str(CREDENTIAL_PATH))
    if not gauth.credentials or gauth.access_token_expired:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(str(CREDENTIAL_PATH))

    drive = GoogleDrive(gauth)
    folder_id = "1bJyt5g4C0I054B8viTvOzSLac1ksq0Wc"
    file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(filename)
    file_drive.Upload()
    print(f"Imagen subida a Google Drive: {filename}")


