import httpx
from nprOlusolaBe.configs import settings as config


endpoint = {
    "transfers_recipient": {
        "create": "transferrecipient",
        "bulk_create": "transferrecipient/bulk",
    },
    "transaction": {
        "create": "transaction/initialize",
        "verify": "transaction/verify",
        "authorized_charge": "transaction/charge_authorization",
    },
    "refund": {
        "create": "refund",
        "verify": "transaction/verify",
    },
    

}


class Client:
    def __init__(
        self,
        base_url: str = "https://api.paystack.co",
    ):
        self.endpoints = endpoint
        self.base_url = base_url
        self.request = httpx.AsyncClient(
            base_url=self.base_url,
            headers=dict(**self.get_header()),
        )

    def get_header(self) -> dict:
        return {
            "Authorization": f"Bearer {config.paystack_secret_key}",
            "Content-type": "application/json",
        }
