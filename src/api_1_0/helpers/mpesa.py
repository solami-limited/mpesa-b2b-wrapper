import base64
import os
import requests
from threading import Thread
from typing import Any, Tuple, Dict
from flask import current_app
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from requests.auth import HTTPBasicAuth
from src import db
from src.api_1_0.models.b2b import B2B, StatusEnum


class MPESA:
    """A class that handles all MPESA related transactions."""
    def __init__(self, req: dict):
        """Initializes the MPESA class."""
        self.data = req
        # final response template to be returned to the client
        self.response = dict(status_message='', status_code=0, account_reference=self.data['pnr'])

    def initiate_b2b(self) -> Tuple[dict, bool]:
        """Initiates a B2B payment."""
        with current_app.app_context():
            record = B2B.query.filter_by(pnr=self.data['pnr']).first()
            if record is None:
                endpoint = '{}/mpesa/b2b/v1/remittax'.format(os.environ.get('B2B_BASE_URL'))
                payload = self._build_b2b_payload(current_app.config['CERTIFICATE'])
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer {}'.format(MPESA.generate_access_token())
                }
                try:
                    response = requests.post(url=endpoint, json=payload, headers=headers)
                    if response.status_code == requests.codes.ok:
                        response = response.json()
                except (requests.ConnectTimeout, requests.ConnectionError, Exception) as e:
                    error = str(e)
                if error or response.get('errorCode') \
                        or response.get('ResponseCode', -1) != current_app.config['MPESA_B2B_SUCCESS_CODE']:
                    self.response['status_message'] = 'Failed to initiate B2B payment.'
                    self.response['status_code'] = current_app.config['GENERIC_FAILURE_CODE']
                    return self.response, True
                # save the B2B payment record by spawning a new thread
                Thread(
                    target=self._create_b2b_payment,
                    args=(response['OriginatorConversationID'], response['ConversationID'])
                ).start()
                # formulate a success response message
                self.response['status_message'] = 'B2B payment initiated successfully.'
                return self.response, False
            # formulate a generic failure response
            self.response['status_message'] = 'Cannot initiate B2B payment. PNR already exists.'
            self.response['status_code'] = current_app.config['GENERIC_FAILURE_CODE']
            return self.response, True

    def _build_b2b_payload(self, certificate: str) -> Dict[str, str]:
        """Builds the payload for the B2B request."""
        return {
            'Initiator': os.environ.get('B2B_INITIATOR'),
            'SecurityCredential': MPESA.rsa_encrypt(current_app.config['B2C_INITIATOR_PASSWORD'], certificate),
            'CommandID': os.environ.get('B2B_COMMAND_ID'),
            'Amount': self.data['amount'],
            'PartyA': os.environ.get('B2B_SHORT_CODE'),
            'PartyB': os.environ.get('PAY_TAX_CODE'),
            'Remarks': 'B2B payment.',
            'QueueTimeOutURL': '{}/payment/timeout'.format(os.environ.get('BASE_URL')),
            'ResultURL': '{}/payment/confirm'.format(os.environ.get('BASE_URL')),
            'AccountReference': self.data['pnr']
        }

    def _create_b2b_payment(self, originator_conversation_id: str, conversation_id: str) -> None:
        """Saves the B2B payment record."""
        record = B2B(
            amount=self.data['amount'],
            pnr=self.data['pnr'],
            originator_conversation_id=originator_conversation_id,
            conversation_id=conversation_id
        )
        db.session.add(record)
        db.session.commit()

    @staticmethod
    def update_b2b_payment(ctx: Any, req: Dict) -> None:
        """Updates the B2B payment record."""
        with ctx.app_context():
            record = B2B.query\
                .filter_by(conversation_id=req.get('ConversationID', '-1'))\
                .filter_by(originator_conversation_id=req.get('OriginatorConversationID', '-1'))\
                .order_by(B2B.id.desc())\
                .first()
            if record and record.status == 'PENDING':
                record.status = StatusEnum.SUCCESS.value if req.get('ResultCode') == 0\
                    else StatusEnum.FAILED.value
                db.session.commit()

    @staticmethod
    def rsa_encrypt(password: str, certificate: str) -> str:
        """Encrypts the password using the certificate provided."""
        with current_app.app_context():
            encryption = ''
            try:
                with open(certificate, 'rb') as f:
                    cert = RSA.importKey(f.read())
                cipher = PKCS1_v1_5.new(cert)
                encryption = base64.b64encode(cipher.encrypt(password.encode('utf-8'))).decode('utf-8')
            except (FileNotFoundError, Exception) as _:
                pass
            return encryption

    @staticmethod
    def generate_access_token() -> str:
        """Generates an access token for the B2B request."""
        token = ''
        try:
            response = requests.get(
                url='{}/oauth/v1/generate?grant_type=client_credentials'.format(os.environ.get('B2B_BASE_URL')),
                auth=HTTPBasicAuth(os.environ.get('B2B_ACCESS_KEY'), os.environ.get('B2B_CONSUMER_SECRET'))
            )
            if response.status_code == requests.codes.ok:
                token = response.json()['access_token']
        except (requests.ConnectTimeout, requests.ConnectionError, Exception) as _:  # noqa
            pass
        return token
