from flask import Blueprint, request, jsonify
from datetime import datetime
from http import HTTPStatus
import logging
from typing import Dict, Tuple

from utils import log_activity, generate_llm_response

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/api/v1/chat", methods=["POST"])
def llm_chat() -> Tuple[Dict, int]:
    """
    Handle LLM chat requests.
    
    Expected JSON payload:
    {
        "username": str,
        "input1": str,
        "input2": str
    }
    """
    try:
        data = request.get_json()
        
        if not all(key in data for key in ["username", "input1", "input2"]):
            return jsonify({
                "error": "Missing required fields"
            }), HTTPStatus.BAD_REQUEST
        
        username = data["username"]
        input1 = data["input1"]
        input2 = data["input2"]
        
        # Generate response
        llm_response = generate_llm_response(input1, input2)
        
        # Log the chat activity
        log_activity(
            username=username,
            action="chat",
            details={
                "input1": input1,
                "input2": input2,
                "response": llm_response
            }
        )
        
        return jsonify({
            "username": username,
            "response": llm_response,
            "timestamp": datetime.utcnow().isoformat()
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error in llm_chat: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR
