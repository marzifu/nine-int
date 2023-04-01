import midtransclient
from .config import settings

class MidtransAPI:
    def __init__(self, is_production):
        self.client = midtransclient.CoreApi(
            is_production=is_production,
            server_key=settings.server_key,
            client_key=settings.client_key
        )

    def create_transaction(self, order_id, gross_amount):
        transaction_details = {
            'order_id': order_id,
            'gross_amount': gross_amount
        }

        payment_response = self.client.charge(transaction_details)
        payment_url = payment_response['redirect_url']

        return payment_url

    def check_payment_status(self, order_id):
        payment_response = self.client.check_payment(order_id)
        return payment_response.status_code