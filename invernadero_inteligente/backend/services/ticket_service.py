import uuid
from datetime import datetime
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB
from invernadero_inteligente.backend.services.gmail_service import GmailService
from datetime import datetime

class TicketService:
    @staticmethod
    def crear_ticket(data):
        ticket_id = str(uuid.uuid4())[:8]
        hoja = GoogleSheetsDB().get_worksheet("tickets")

        if len(hoja.get_all_values()) == 0:
            hoja.append_row([
                "ticket_id", "Dispositivo", "Email", "Asunto",
                "Descripcion", "FechaCreacion", "Responsable", "Status"
            ])

        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        hoja.append_row([
            ticket_id,
            data.get("dispositivo", ""),
            data.get("email", ""),
            data.get("asunto", ""),
            data.get("descripcion", ""),
            fecha_creacion,
            "",  # Responsable
            "Activo"
        ])

        # === Enviar correo ===
        try:
            gmail = GmailService()
            asunto = f"[Ticket #{ticket_id}] Nuevo ticket de soporte"
            cuerpo = (
                f"Se ha creado un nuevo ticket de soporte:\n\n"
                f"🆔 Ticket ID: {ticket_id}\n"
                f"📦 Dispositivo: {data.get('dispositivo', '')}\n"
                f"📧 Usuario: {data.get('email', '')}\n"
                f"📝 Asunto: {data.get('asunto', '')}\n"
                f"📄 Descripción:\n{data.get('descripcion', '')}\n\n"
                f"📅 Fecha: {fecha_creacion}\n"
            )
            gmail.enviar_correo(
                destinatario="greenieinvernadero@gmail.com",
                asunto=asunto,
                cuerpo=cuerpo
            )
        except Exception as e:
            print(f"[ERROR] Falló el envío de correo: {e}")

        return ticket_id
