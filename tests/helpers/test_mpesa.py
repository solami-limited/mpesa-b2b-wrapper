import uuid
from random import randint
from typing import Tuple
from unittest.mock import MagicMock
from src.api_1_0.helpers.mpesa import MPESA

# the mpesa object to be used in the tests
m = MPESA(
    {
        'amount': 100,
        'pnr': randint(100000, 999999)
    }
)

# endpoint
endpoint = 'http://localhost:8080/mpesa/b2b/v1/remittax'

# headers
headers = {
    'Authorization': 'Bearer mock_token',
    'Content-Type': 'application/json'
}

# json payload
payload = {
    'AccountReference': m.data['pnr'],
    'Amount': m.data['amount'],
    'CommandID': '6ytx',
    'Initiator': 'Safaricom',
    'PartyA': '222',
    'PartyB': 'Tax123@example',
    'QueueTimeOutURL': 'http://localhost:5000/api/v1.0/payment/timeout',
    'Remarks': 'B2B payment.',
    'ResultURL': 'http://localhost:5000/api/v1.0/payment/confirm',
    'SecurityCredential': 'mock_encrypted_password'
}

# a mock successful response from the B2B API
mock_successful_response = {
    'ConversationID': f'AG_{randint(1000, 9999)}_{uuid.uuid4().hex}',
    'OriginatorConversationID': f'{randint(10, 99)}-{randint(2222, 9999)}-{randint(1, 9)}',
    'ResponseCode': '0',
    'ResponseDescription': 'Accept the service request successfully.'
}

mock_unsuccessful_response = {
    'requestId': f'{randint(2222, 9999)}-{randint(222222, 999999)}-{randint(1, 9)}',
    'errorCode': f'{randint(100, 401)}.{randint(1000, 9999)}.{randint(1, 9)}',
    'errorMessage': 'An error occurred while processing the request.'
}


def test_make_successful_initiate_b2b_call(app, mocker):
    """Test that the initiate_b2b method makes a successful call to the B2B API."""
    with app.app_context():
        response, _, mock_requests = generic_mocking(mocker, 200, mock_successful_response)
        # assert the mock_requests method was called
        mock_requests.assert_called_once()
        # assert the mock_requests method was called with the correct arguments
        mock_requests.assert_called_with(url=endpoint, headers=headers, json=payload)
        assert response['status_message'] == 'B2B payment initiated successfully.'
        assert response['status_code'] == '0'
        assert response['account_reference'] == m.data['pnr']


def test_make_unsuccessful_initiate_b2b_call(app, mocker):
    """Test that B2B API returns an error and the initiate_b2b method handles it."""
    with app.app_context():
        response, _, _ = generic_mocking(mocker, 200, mock_unsuccessful_response)
        assert response['status_message'] == 'An error occurred while processing the request.'
        assert response['status_code'] == '999'
        assert response['account_reference'] == m.data['pnr']


def generic_mocking(mocker: MagicMock, status_code: int, mock_response: dict) -> Tuple[dict, bool, MagicMock]:
    """Generic mocking for the initiate_b2b method."""
    # mock the first method of the query object
    mocker.patch('sqlalchemy.orm.query.Query.first', return_value=None)
    # mock the Thread class
    mocker.patch('src.api_1_0.helpers.mpesa.Thread')
    # mock the generate_access_token method
    mocker.patch('src.api_1_0.helpers.mpesa.MPESA.generate_access_token', return_value='mock_token')
    # mock the rsa_encrypt method
    mocker.patch('src.api_1_0.helpers.mpesa.MPESA.rsa_encrypt', return_value='mock_encrypted_password')
    # mock the requests.post method
    mock_requests = mocker.patch('requests.post')
    mock_requests.return_value.status_code = status_code
    mock_requests.return_value.json.return_value = mock_response
    # make the call
    response, error = m.initiate_b2b()
    return response, error, mock_requests  # return the response, error and mock_requests object
