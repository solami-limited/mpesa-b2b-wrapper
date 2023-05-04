import pytz
from threading import Thread
from datetime import datetime
from typing import Dict, Any
from flask import request, current_app
from src.api_1_0 import api_bp
from src.api_1_0.helpers.mpesa import MPESA
from src.api_1_0.helpers.validator import Validator
from src.api_1_0.routes.error import bad_request


@api_bp.route('/payment/initiate', methods=['POST'])
def index():
    """Handle the initiation of a payment"""
    data, error_message = Validator.validate(request.get_json(silent=True))
    if error_message:
        # return a bad request response with the error message
        return bad_request(error_message)
    response, error = MPESA(data).initiate_b2b()
    status_code = 400 if error else 201
    return response, status_code


@api_bp.route('payment/confirm', methods=['POST'])
def confirm(req: Dict[str, Any] = None):
    """Handle the confirmation of a payment"""
    data = request.get_json(silent=True) if not req else req
    tpt = datetime.now(pytz.timezone(current_app.config['TIME_ZONE']))\
        .strftime(current_app.config['TIME_FORMAT'])
    # final response template to be returned to the client
    response = {
        'ResultCode': current_app.config['MPESA_B2B_FAILURE_CODE'],
        'ResultDesc': 'Confirmation payload received successfully.',
        'ThirdPartyTransID': tpt
    }
    # check if the request payload has the Result key
    if not data.get('Result'):
        response['ResultCode'] = current_app.config['GENERIC_FAILURE_CODE']
        response['ResultDesc'] = 'Invalid request payload.'
        return response, 400
    # check if the ResultCode is 0
    if data['Result']['ResultCode'] == current_app.config['MPESA_B2B_SUCCESS_CODE']:
        response['ResultCode'] = current_app.config['MPESA_B2B_SUCCESS_CODE']
    # spawn a new thread to handle the confirmation
    Thread(
        target=MPESA.update_b2b_payment,
        args=(current_app._get_current_object(), data['Result'])
    ).start()
    # we can safely return a response to the caller
    return response


@api_bp.route('payment/timeout', methods=['POST'])
def timeout():
    # See: https://developer.safaricom.co.ke/Documentation
    # ‼️NOT SURE ABOUT THIS METHOD ‼️
    # It doesn't seem different from the 'confirm()' method/function above ☝
    # Assuming, we get the same payload as 'confirm()',
    # we can pass the request to 'confirm()' and return the response
    return confirm(request.get_json(silent=True))
