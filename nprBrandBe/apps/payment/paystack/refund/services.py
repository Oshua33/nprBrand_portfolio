from nprOlusolaBe.apps.payment.paystack.charge import schemas
from nprOlusolaBe.apps.payment.paystack.paystack_base import (
    Client,
    endpoint,
)
from nprOlusolaBe.utils.base_response import get_error_response


class PaymentRefund:
    client = Client()
    urls = endpoint["refund"]

    @classmethod
    async def create_refund(
        cls,
        payload: schemas.RefundTransactionIn,
    ) -> schemas.IRefundSingleResponse:
        try:
            response = await cls.client.request.post(
                url=cls.urls.get("create"),
                json=payload.model_dump(),
            )
            return response.json()
        except Exception as e:
            raise get_error_response(detail="Error refunding transaction") from e

    @classmethod
    async def get_refund(cls, reference_code: str) -> schemas.IRefundSingleResponse:
        try:
            response = await cls.client.request.post(
                url=f'{cls.urls.get("create")}/{reference_code}'
            )

            return response.json()
        except Exception as e:
            raise get_error_response("Error listing refunds") from e
