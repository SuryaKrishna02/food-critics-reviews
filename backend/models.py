from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class ChatResponse:
    """Data class for chat response structure."""
    username: str
    message: str
    timestamp: datetime

@dataclass
class ActivityLog:
    """Data class for activity log structure."""
    action: str
    timestamp: datetime
    details: Dict

# Store data in memory (replace with database in production)
chat_history: List[ChatResponse] = []
activity_logs: List[Dict] = []
