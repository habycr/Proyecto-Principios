from invernadero_inteligente.backend.services.gmail_service import GmailService

if __name__ == "__main__":
    gmail = GmailService()
    gmail.enviar_correo(
        destinatario="correo_ficticio@example.com",
        asunto="Prueba inicial",
        cuerpo="Este es un correo de prueba enviado desde la API de Gmail."
    )
    print("Correo enviado y token guardado.")
