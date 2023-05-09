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
        self.response = dict(status_message='', status_code='', account_reference=self.data['pnr'])

    def initiate_b2b(self) -> Tuple[dict, bool]:
        """Initiates a B2B payment."""
        with current_app.app_context():
            current_app.logger.info(f"{self.data['pnr']=} | Initiating B2B payment...")
            record = B2B.query.filter_by(pnr=self.data['pnr']).first()
            if record is None:
                endpoint = '{}/mpesa/b2b/v1/remittax'.format(os.environ.get('B2B_BASE_URL'))
                payload = self._build_b2b_payload(current_app.config['CERTIFICATE'])
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer {}'.format(MPESA.generate_access_token())
                }
                response, err = dict(), ''
                try:
                    response = requests.post(url=endpoint, json=payload, headers=headers)
                    if response.status_code in (requests.codes.ok, requests.codes.created, requests.codes.bad_request):
                        response = response.json()
                    current_app.logger.info(f"{self.data['pnr']=} | B2B API response ~>\n\t{response}")
                except (requests.ConnectTimeout, requests.ConnectionError, Exception) as e:
                    current_app.logger.error(f"{self.data['pnr']=} | An error occurred "
                                             f"while initiating B2B payment ~>\n\t{e}")
                    err = f'An error occurred while initiating B2B payment: {e}'
                if err or response.get('errorCode'):
                    current_app.logger.error(f"{self.data['pnr']=} | Failed to initiate B2B payment")
                    self.response['status_code'] = current_app.config['GENERIC_FAILURE_CODE']
                    self.response['status_message'] = 'Failed to initiate B2B payment.'
                    if response.get('errorMessage'):
                        self.response['status_message'] = response['errorMessage']
                    return self.response, True
                current_app.logger.info(f" {self.data['pnr']=} | B2B payment initiated successfully")
                # save the B2B payment record by spawning a new thread
                Thread(
                    target=self._create_b2b_payment,
                    args=(current_app._get_current_object(), response['OriginatorConversationID'],
                          response['ConversationID'])
                ).start()
                # formulate a success response message
                self.response['status_code'] = current_app.config['MPESA_B2B_SUCCESS_CODE']
                self.response['status_message'] = 'B2B payment initiated successfully.'
                return self.response, False
            # formulate a generic failure response
            current_app.logger.error(f" {self.data['pnr']=} | A similar B2B payment already exists.")
            self.response['status_code'] = current_app.config['GENERIC_FAILURE_CODE']
            self.response['status_message'] = 'A similar B2B payment already exists.'
            return self.response, True

    def _build_b2b_payload(self, certificate: str) -> Dict[str, str]:
        """Builds the payload for the B2B request."""
        return {
            'Initiator': os.environ.get('B2B_INITIATOR'),
            'SecurityCredential': MPESA.rsa_encrypt(os.environ.get('B2B_INITIATOR_PASSWORD'), certificate),
            'CommandID': os.environ.get('B2B_COMMAND_ID'),
            'Amount': self.data['amount'],
            'PartyA': os.environ.get('B2B_SHORT_CODE'),
            'PartyB': os.environ.get('PAY_TAX_CODE'),
            'Remarks': 'B2B payment.',
            'QueueTimeOutURL': '{}/payment/timeout'.format(os.environ.get('BASE_URL')),
            'ResultURL': '{}/payment/confirm'.format(os.environ.get('BASE_URL')),
            'AccountReference': self.data['pnr']
        }

    def _create_b2b_payment(self, ctx: Any, originator_conversation_id: str, conversation_id: str) -> None:
        """Saves the B2B payment record."""
        with ctx.app_context():
            ctx.logger.info(f"{self.data['pnr']=} | Saving B2B payment record...")
            record = B2B(
                amount=self.data['amount'],
                pnr=self.data['pnr'],
                originator_conversation_id=originator_conversation_id,
                conversation_id=conversation_id
            )
            db.session.add(record)
            db.session.commit()
            ctx.logger.info(f"{self.data['pnr']=} | B2B payment record saved successfully.")

    @staticmethod
    def update_b2b_payment(ctx: Any, req: Dict) -> None:
        """Updates the B2B payment record."""
        with ctx.app_context():
            ctx.logger.info(f"{req.get('ConversationID')=} | Updating B2B payment record...")
            record = B2B.query\
                .filter_by(conversation_id=req.get('ConversationID', '-1'))\
                .filter_by(originator_conversation_id=req.get('OriginatorConversationID', '-1'))\
                .order_by(B2B.id.desc())\
                .first()
            if record and record.status == StatusEnum.PENDING:
                record.status = StatusEnum.SUCCESS if req.get('ResultCode') == 0 else StatusEnum.FAILED
                db.session.commit()
                ctx.logger.info(f"{req.get('ConversationID')=} | B2B payment record updated successfully.")
            else:
                ctx.logger.error(f"{req.get('ConversationID')=} | Transaction record not "
                                 f"found or already in a final state.")

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
