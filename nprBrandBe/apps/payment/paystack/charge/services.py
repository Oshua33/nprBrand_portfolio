from nprOlusolaBe.apps.payment.paystack.charge import schemas
from nprOlusolaBe.apps.payment.paystack.paystack_base import (
    Client,
    endpoint,
)

from nprOlusolaBe.utils.base_response import get_error_response


class TransactionCharge:
    client = Client()
    urls = endpoint["transaction"]

    @classmethod
    async def create_charge(
        cls, payload: schemas.IChargeRequest
    ) -> schemas.IChargeRequestOut:
        try:
            response = await cls.client.request.post(
                url=cls.urls.get("create"),
                json=payload.model_dump(),
            )
            data = response.json()
            if not data["status"]:
                raise get_error_response(
                    detail=data["message"],
                    status_code=response.status_code,
                )
            return schemas.IChargeRequestOut(**data)
        except Exception as e:
            raise e

    @classmethod
    async def create_authorized_charge(
        cls, payload: schemas.ISavedCardChargeIn
    ) -> schemas.IChargeRequestOut:
        try:
            response = await cls.client.request.post(
                url=cls.urls.get("authorized_charge"),
                json=payload.model_dump(),
            )
            data = response.json()
            if not data["status"]:
                raise get_error_response(
                    detail=data["message"],
                    status_code=response.status_code,
                )
            return data
        except Exception as e:
            raise e

    @classmethod
    async def charge_verification(cls, payment_reference: str):
        try:
            url = f'{cls.urls.get("verify")}/{payment_reference}'
            response = await cls.client.request.get(
                url=url,
            )
            data = response.json()
            if not data["status"]:
                raise get_error_response(
                    detail=data["message"],
                    status_code=response.status_code,
                )
            return schemas.IChargeResponse(**data)
        except Exception as e:
            raise e
