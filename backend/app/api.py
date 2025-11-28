"""
Flask API for Padel Court Availability Search Service
MVP with JWT authentication
"""

import logging
from datetime import UTC, datetime

from flask import Flask, jsonify
from flask_cors import CORS

# Import scheduler module to initialize background tasks
import app.scheduler

# Import scheduler to initialize it
from app.config import CORS_ORIGINS, DEBUG, HOST, JWT_EXPIRATION_HOURS, PORT, SECRET_KEY
from app.courtfinder import PadelMateService
from app.routes.admin import admin_bp
from app.routes.auth import auth_bp
from app.routes.locations import locations_bp
from app.routes.search import search_bp
from app.routes.search_orders import search_orders_bp
from app.routes.tasks import tasks_bp
from app.services import AvailabilityService

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

# Configuration
app.config["SECRET_KEY"] = SECRET_KEY
app.config["JWT_EXPIRATION_HOURS"] = JWT_EXPIRATION_HOURS

# Initialize services
padel_service = PadelMateService()
availability_service = AvailabilityService()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(search_bp)
app.register_blueprint(search_orders_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(tasks_bp)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Health check
@app.route("/health", methods=["GET"])
def health():
    return (
        jsonify({"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}),
        200,
    )


if __name__ == "__main__":
    # Development server
    app.run(debug=DEBUG, host=HOST, port=PORT)
