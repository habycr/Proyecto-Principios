import os
import base64
from google.auth.transport.requests import Request
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from invernadero_inteligente.backend.config.settings import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self):
        self.creds = None
        if os.path.exists(GMAIL_TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_PATH, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(GMAIL_TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('gmail', 'v1', credentials=self.creds)

    def enviar_correo(self, destinatario, asunto, cuerpo):
        mensaje = EmailMessage()
        mensaje.set_content(cuerpo)
        mensaje['To'] = destinatario
        mensaje['From'] = "me"
        mensaje['Subject'] = asunto

        mensaje_bytes = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
        body = {'raw': mensaje_bytes}

        self.service.users().messages().send(userId='me', body=body).execute()
