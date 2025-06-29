# backend/services/google_sheets.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from invernadero_inteligente.frontend.config import config
from typing import List, Dict, Optional, Union
from datetime import datetime

class GoogleSheetsDB:
    def __init__(self):
        """Inicializa la conexión con Google Sheets"""
        self.GSHEETS_CREDENTIALS = config.GSHEETS_CREDENTIALS
        self.SPREADSHEET_ID = '1YxZ4E-lidhnCogh3G2gTST8ONTm6_9JV7zYbQh7z4Ms'  # Solo el ID

        if not self.GSHEETS_CREDENTIALS.exists():
            raise FileNotFoundError(f"Credenciales no encontradas en: {self.GSHEETS_CREDENTIALS}")

        # Configurar el alcance de la API
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Autenticar y crear cliente
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            str(self.GSHEETS_CREDENTIALS), self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(self.SPREADSHEET_ID)

    def get_worksheet(self, name: str) -> gspread.Worksheet:
        """
        Obtiene una hoja por nombre, la crea si no existe

        Args:
            name: Nombre de la hoja de cálculo

        Returns:
            Objeto Worksheet de gspread
        """
        try:
            return self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            # Crear nueva hoja si no existe
            return self.sheet.add_worksheet(title=name, rows=100, cols=20)
            # Si es la hoja de historial, agregar encabezados
            if name == "historial":
                headers = ["Fecha", "Ticket ID", "Dispositivo", "Campo", "Valor Anterior", "Valor Nuevo"]
                new_worksheet.append_row(headers)

            return new_worksheet

        except Exception as e:
            raise Exception(f"Error al obtener hoja {name}: {str(e)}")

    def get_tickets(self) -> List[Dict]:
        """
        Obtiene todos los tickets de la hoja 'tickets'

        Returns:
            Lista de diccionarios con los tickets
        """
        try:
            worksheet = self.get_worksheet("tickets")
            return worksheet.get_all_records()
        except Exception as e:
            raise Exception(f"Error al obtener tickets: {str(e)}")

    def update_ticket(self, ticket_id: str, updates: Dict) -> bool:
        """
        Actualiza un ticket específico

        Args:
            ticket_id: ID del ticket a actualizar
            updates: Diccionario con campos a actualizar {campo: valor}

        Returns:
            True si la actualización fue exitosa

        Raises:
            ValueError: Si el ticket no existe
            Exception: Si ocurre un error en la actualización
        """
        try:
            worksheet = self.get_worksheet("tickets")
            cell = worksheet.find(ticket_id)

            if not cell:
                raise ValueError(f"Ticket con ID {ticket_id} no encontrado")

            row = cell.row
            headers = worksheet.row_values(1)

            # Preparar actualizaciones en batch
            batch_updates = []
            for key, value in updates.items():
                if key in headers:
                    col = headers.index(key) + 1  # Las columnas empiezan en 1
                    batch_updates.append({
                        'range': gspread.utils.rowcol_to_a1(row, col),
                        'values': [[value]]
                    })

            # Ejecutar actualizaciones en batch
            if batch_updates:
                worksheet.batch_update(batch_updates)

            return True
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise Exception(f"Error al actualizar ticket {ticket_id}: {str(e)}")

    def create_ticket(self, ticket_data: Dict) -> str:
        """
        Crea un nuevo ticket en la hoja

        Args:
            ticket_data: Diccionario con los datos del ticket

        Returns:
            ID del ticket creado
        """
        try:
            worksheet = self.get_worksheet("tickets")

            # Si la hoja está vacía, agregar encabezados
            if not worksheet.get_all_values():
                headers = list(ticket_data.keys())
                worksheet.append_row(headers)

            # Agregar nuevo ticket
            values = [ticket_data.get(header, "") for header in worksheet.row_values(1)]
            worksheet.append_row(values)

            return ticket_data.get('ticket_id', '')
        except Exception as e:
            raise Exception(f"Error al crear ticket: {str(e)}")

    def search_tickets(self, search_term: str, column: str = "Asunto") -> List[Dict]:
        """
        Busca tickets que coincidan con el término de búsqueda

        Args:
            search_term: Término a buscar
            column: Columna donde buscar (por defecto "Asunto")

        Returns:
            Lista de tickets que coinciden con la búsqueda
        """
        try:
            worksheet = self.get_worksheet("tickets")
            records = worksheet.get_all_records()

            return [ticket for ticket in records
                    if search_term.lower() in str(ticket.get(column, "")).lower()]
        except Exception as e:
            raise Exception(f"Error en búsqueda de tickets: {str(e)}")

    def get_historial(self) -> List[Dict]:
        """
        Obtiene todo el historial de cambios de la hoja 'Historial'

        Returns:
            Lista de diccionarios con el historial
        """
        try:
            worksheet = self.get_worksheet("Historial")  # O el nombre de tu hoja
            return worksheet.get_all_records()
        except Exception as e:
            raise Exception(f"Error al obtener historial: {str(e)}")

    def add_historial_entry(self, entry_data: Dict) -> bool:
        """
        Añade una nueva entrada al historial

        Args:
            entry_data: Diccionario con los datos del cambio
                        Debe contener: ticket_id, dispositivo, campo,
                                       anterior, nuevo, fecha, usuario

        Returns:
            True si se añadió correctamente
        """
        try:
            worksheet = self.get_worksheet("Historial")  # O el nombre de tu hoja

            # Si la hoja está vacía, agregar encabezados
            if not worksheet.get_all_values():
                headers = ["fecha", "ticket_id", "dispositivo", "campo",
                           "anterior", "nuevo", "usuario"]
                worksheet.append_row(headers)

            # Preparar los valores en el orden correcto
            values = [
                entry_data.get("fecha", ""),
                entry_data.get("ticket_id", ""),
                entry_data.get("dispositivo", ""),
                entry_data.get("campo", ""),
                entry_data.get("anterior", ""),
                entry_data.get("nuevo", ""),
                entry_data.get("usuario", "")
            ]

            worksheet.append_row(values)
            return True
        except Exception as e:
            raise Exception(f"Error al añadir entrada al historial: {str(e)}")

    def registrar_cambio_historial(self, ticket_id: str, dispositivo: str, campo: str,
                                   valor_anterior: str, valor_nuevo: str) -> bool:
        """
        Registra un cambio en el historial de modificaciones

        Args:
            ticket_id: ID del ticket modificado
            dispositivo: Nombre del dispositivo asociado
            campo: Campo que fue modificado
            valor_anterior: Valor antes del cambio
            valor_nuevo: Valor después del cambio

        Returns:
            True si el registro fue exitoso
        """
        try:
            worksheet = self.get_worksheet("historial")

            # Formatear fecha actual
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Preparar datos para insertar
            datos = [
                fecha,
                str(ticket_id),
                str(dispositivo),
                str(campo),
                str(valor_anterior),
                str(valor_nuevo)
            ]

            # Insertar en la primera fila disponible
            worksheet.append_row(datos)
            return True
        except Exception as e:
            raise Exception(f"Error al registrar cambio en historial: {str(e)}")

    def obtener_historial(self, ticket_id: str = None, limit: int = 10) -> List[Dict]:
        """
        Obtiene el historial de cambios, opcionalmente filtrado por ticket_id

        Args:
            ticket_id: ID del ticket para filtrar (opcional)
            limit: Número máximo de registros a devolver

        Returns:
            Lista de diccionarios con el historial
        """
        try:
            worksheet = self.get_worksheet("Historial Tickets")
            registros = worksheet.get_all_records()

            # Ordenar por fecha (más reciente primero)
            registros.sort(key=lambda x: datetime.strptime(x['Fecha'], "%d/%m/%Y %H:%M:%S"), reverse=True)

            # Filtrar por ticket_id si se especifica
            if ticket_id:
                registros = [r for r in registros if str(r['Ticket ID']) == str(ticket_id)]

            return registros[:limit]
        except Exception as e:
            raise Exception(f"Error al obtener historial: {str(e)}")

        def get_worksheet(self, name: str) -> gspread.Worksheet:
            """
            Obtiene una hoja por nombre, la crea si no existe

            Args:
                name: Nombre de la hoja de cálculo

            Returns:
                Objeto Worksheet de gspread
            """
            try:
                # Primero intenta obtener la hoja existente
                return self.sheet.worksheet(name)
            except gspread.exceptions.WorksheetNotFound:
                try:
                    # Verifica si el nombre es válido
                    if not name or not isinstance(name, str) or len(name) > 100:
                        raise ValueError("Nombre de hoja no válido")

                    # Verifica si ya existe una hoja con ese nombre (por si acaso)
                    existing_sheets = [ws.title for ws in self.sheet.worksheets()]
                    if name in existing_sheets:
                        return self.sheet.worksheet(name)

                    # Crear nueva hoja si no existe
                    new_worksheet = self.sheet.add_worksheet(
                        title=name,
                        rows=100,
                        cols=20
                    )

                    # Si es la hoja de historial, agregar encabezados
                    if name.lower() == "Historial tickets":
                        headers = ["Fecha", "Ticket ID", "Dispositivo", "Campo", "Valor Anterior", "Valor Nuevo"]
                        new_worksheet.append_row(headers)

                    return new_worksheet
                except Exception as e:
                    # Si falla la creación, intenta usar la primera hoja como fallback
                    try:
                        return self.sheet.get_worksheet(0)
                    except:
                        raise Exception(f"No se pudo crear ni obtener hoja: {str(e)}")
            except Exception as e:
                raise Exception(f"Error al obtener hoja {name}: {str(e)}")