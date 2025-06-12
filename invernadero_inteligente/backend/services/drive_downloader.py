# Librerías necesarias para autenticación y acceso a Google Drive
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os, io
from pathlib import Path

# Alcance de permisos: solo lectura del contenido de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Carpeta local donde se guardarán las imágenes descargadas
IMAGE_DIR = Path("timelapse_images")
IMAGE_DIR.mkdir(exist_ok=True)  # Crea la carpeta si no existe

# ID de la carpeta de Google Drive
FOLDER_ID = "1bJyt5g4C0I054B8viTvOzSLac1ksq0Wc"

def authenticate_drive():
    """
    Maneja la autenticación con Google usando OAuth2.
    Guarda un token de sesión en 'token.json' para que no pida permisos cada vez.
    """
    creds = None

    # Si ya existe un token guardado, lo usamos
    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Si no hay token válido, pedimos al usuario que autorice
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh()  # Si el token expiró pero se puede refrescar
        else:
            # Flujo de autenticación local: abre navegador para pedir permisos
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardamos el token para futuras ejecuciones
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Creamos el cliente de la API de Google Drive
    return build("drive", "v3", credentials=creds)

def download_images_from_drive(service):
    """
    Lista los archivos JPEG en la carpeta de Google Drive y descarga los que no existan localmente.
    """
    # Consulta a la API de Drive: solo imágenes JPEG dentro de la carpeta indicada
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='image/jpeg'",
        spaces='drive',
        fields="files(id, name)",     # Solo necesitamos el ID y nombre de los archivos
        orderBy="createdTime desc"    # Ordenar por fecha de creación más reciente
    ).execute()

    # Iteramos sobre cada archivo encontrado
    for file in results.get("files", []):
        local_file = IMAGE_DIR / file["name"]

        # Solo descargamos si no existe ya localmente
        if not local_file.exists():
            # Obtenemos el archivo como un stream binario
            request = service.files().get_media(fileId=file["id"])
            with open(local_file, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                print(f"Descargada: {file['name']}")

# Punto de entrada del script
if __name__ == "__main__":
    # Autenticamos con Google
    service = authenticate_drive()
    # Descargamos las imágenes JPEG desde la carpeta
    download_images_from_drive(service)
