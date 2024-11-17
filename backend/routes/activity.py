from flask import Blueprint, jsonify
from http import HTTPStatus
import logging
from typing import Dict, Tuple

from models import activity_logs

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
activity_bp = Blueprint('activity', __name__)

@activity_bp.route("/api/v1/activity/<username>", methods=["GET"])
def get_past_activity(username: str) -> Tuple[Dict, int]:
    """
    Retrieve past activity for a specific user.
    
    Args:
        username: User's identifier
    """
    try:
        # Filter activities for the specified user
        user_activities = [
            log for log in activity_logs 
            if log["username"] == username
        ]
        
        return jsonify({
            "username": username,
            "activities": user_activities
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Error in get_past_activity: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR
