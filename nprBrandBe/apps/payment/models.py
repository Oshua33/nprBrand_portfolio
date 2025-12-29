from datetime import datetime
from decimal import Decimal
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.apps.payment.paystack.enum import PaymentStatus
from nprOlusolaBe.lib.database.base_model import BaseModel
from nprOlusolaBe.utils.random_string import random_str
import edgy


def get_payment_reference() -> str:
    return f"TR-{random_str(14)}"


class Payment(BaseModel):
    reference: str = edgy.CharField(max_length=20, default=get_payment_reference)
    total: Decimal = edgy.DecimalField(max_digits=10, decimal_places=2)
    order: Order = edgy.ForeignKey(
        Order,
        on_delete=edgy.SET_NULL,
        related_name="payment",
        null=True,
    )
    currency: str = edgy.CharField(max_length=10, default="NGN")
    user: User = edgy.ForeignKey(
        User,
        related_name="payments",
        null=True,
        on_delete=edgy.SET_NULL,
    )
    promo_code: dict = edgy.JSONField(default=[])
    extra_data: dict = edgy.JSONField(default={})
    payment_url: str = edgy.TextField()
    is_trash:bool = edgy.BooleanField(default=False)
    verified_at: datetime = edgy.DateTimeField(default=None, null=True)
    status: str = edgy.CharField(
        max_length=20,
        default=PaymentStatus.INITIALIZE.value,
    )
    is_completed: bool = edgy.BooleanField(default=False)
