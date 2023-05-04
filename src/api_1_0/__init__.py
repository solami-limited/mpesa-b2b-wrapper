from flask import Blueprint

# Create a Blueprint object named 'api' and 'error'
api_bp = Blueprint('api', __name__)
error_bp = Blueprint('error', __name__)

from .routes import main, error
