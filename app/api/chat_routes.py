import logging
from flask import Blueprint, request, jsonify
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)

def create_chat_routes(chatbot_service: ChatbotService) -> Blueprint:
    """Create chat routes with dependency injection."""
    
    chat_bp = Blueprint('chat', __name__)
    
    @chat_bp.route('/api/chat', methods=['POST'])
    def chat():
        """Handle chat API requests."""
        try:
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.get_json()
            if not data or 'messages' not in data:
                return jsonify({"error": "Missing 'messages' field"}), 400
            
            chat_history = data.get('messages', [])
            
            if not isinstance(chat_history, list):
                return jsonify({"error": "Messages must be a list"}), 400
            
            response_content = chatbot_service.process_chat(chat_history)
            
            return jsonify({
                "choices": [{"message": {"content": response_content}}]
            })
            
        except Exception as e:
            logger.error(f"Unexpected error in chat API: {e}")
            return jsonify({
                "choices": [{"message": {"content": "An unexpected error occurred."}}]
            }), 500
    
    return chat_bp
