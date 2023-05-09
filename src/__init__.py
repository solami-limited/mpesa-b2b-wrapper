from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config.default import config

db = SQLAlchemy()


def create_app(config_name):
    """Create an application instance."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)

    @app.before_request
    def log_request_info():
        """Log the request."""
        app.logger.debug('***** Start [REQUEST] *****')
        app.logger.debug(f'[Headers]:\n{request.headers}')
        app.logger.debug(f'[Body]:\n{request.get_data(as_text=True)}')
        app.logger.debug('***** End [REQUEST] *****')

    @app.after_request
    def log_response_info(response):
        """Log the response."""
        app.logger.debug(f'***** [RESPONSE] *****:\n{response.get_data(as_text=True)}')
        return response

    # register blueprints
    from .api_1_0 import error_bp, api_bp
    app.register_blueprint(error_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1.0')
    return app
