from flask import Flask
import logging
from routes.chat import chat_bp
from routes.activity import activity_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(chat_bp)
    app.register_blueprint(activity_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
