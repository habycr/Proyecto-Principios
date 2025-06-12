import pygame
import time
from pathlib import Path
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Clase que permite descargar imágenes de Google Drive y reproducirlas como timelapse en Pygame
class TimelapseViewer:
    def __init__(self, screen, folder_id, cred_path=Path(__file__).parent/"credentials.json", cache_dir="timelapse_cache", secret_path= Path(__file__).parent/"client_secrets.json"):
        self.screen = screen
        self.folder_id = folder_id
        self.cred_path = cred_path
        self.cache_dir = Path(cache_dir)
        self.imagenes = []
        self.secret_path = secret_path

    # Autentica la conexión con Google Drive
    def autenticar_drive(self):
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(str(self.secret_path))
        gauth.LoadCredentialsFile(str(self.cred_path))   # Carga las credenciales si ya existen

        # Si el token está vencido o no existe, pide autenticación y guarda las credenciales actualizadas
        if not gauth.credentials or gauth.access_token_expired:
            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(str(self.cred_path))

        return GoogleDrive(gauth)

    #Descarga las imágenes de la carpeta de Drive
    def descargar_imagenes(self, max_imgs=50):
        self.cache_dir.mkdir(exist_ok=True)         # Crea el directorio si no existe
        drive = self.autenticar_drive()             # Autentica la sesión con Google Drive

        print("Descargando imágenes")
        # Obtiene la lista de archivos .jpg en la carpeta
        file_list = drive.ListFile({
            'q': f"'{self.folder_id}' in parents and trashed=false"
        }).GetList()

        # Filtra los archivos JPG, ordena por nombre (por timestamp en el nombre), y toma los más recientes
        imagenes = sorted(
            [f for f in file_list if f['title'].endswith(".jpg")],
            key=lambda x: x['title'],
            reverse=True
        )[:max_imgs]

        self.imagenes = []
        # Recorre en orden cronológico (más antiguas primero)
        for file in reversed(imagenes):
            local_path = self.cache_dir / file['title']
            # Si el archivo no se ha descargado antes, lo descarga
            if not local_path.exists():
                file.GetContentFile(str(local_path))
            self.imagenes.append(local_path)  # Agrega a la lista local

        print(f"Se descargaron {len(self.imagenes)} imágenes.")

    # Reproduce las imágenes como un video timelapse
    def mostrar_timelapse(self, duracion=0.5):
        if not self.imagenes:
            print("⚠No hay imágenes para mostrar.")
            return

        print("Mostrando timelapse...")
        for img_path in self.imagenes:
            try:
                # Carga la imagen, la escala al tamaño de la pantalla, y la muestra
                img = pygame.image.load(str(img_path)).convert()
                img = pygame.transform.scale(img, self.screen.get_size())
                self.screen.blit(img, (0, 0))
                pygame.display.flip()
                time.sleep(duracion)  # Espera entre imágenes
            except Exception as e:
                print(f"Error cargando {img_path.name}: {e}")
        print("Timelapse finalizado.")
