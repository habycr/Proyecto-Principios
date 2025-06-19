from flask import Blueprint, request, jsonify
from invernadero_inteligente.backend.services.ticket_service import TicketService

ticket_bp = Blueprint("ticket", __name__)

@ticket_bp.route('/ticket', methods=['POST'])
def crear_ticket():
    try:
        data = request.get_json()
        ticket_id = TicketService.crear_ticket(data)
        return jsonify({
            "status": "success",
            "ticket_id": ticket_id,
            "message": "Ticket creado exitosamente"
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al crear el ticket: {str(e)}"
        }), 500
