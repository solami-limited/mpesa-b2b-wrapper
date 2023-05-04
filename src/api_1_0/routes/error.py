from werkzeug.exceptions import NotFound, MethodNotAllowed, HTTPException
from src.api_1_0 import error_bp
from src.api_1_0.helpers.exceptions import ValidationError


@error_bp.errorhandler(ValidationError)
def bad_request(error):
    response = {'error': error}
    return response, 400


@error_bp.app_errorhandler(NotFound)
def not_found():
    response = {'error': 'invalid resource URI.'}
    return response, 404


@error_bp.errorhandler(MethodNotAllowed)
def method_not_supported():
    response = {'error': 'method not supported.'}
    return response, 405


@error_bp.app_errorhandler(HTTPException)
def internal_server_error():
    response = {'error': 'internal server error.'}
    return response, 500
