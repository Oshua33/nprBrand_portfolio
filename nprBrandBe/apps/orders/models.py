import edgy
from nprOlusolaBe.apps.orders.v1.schemas import OrderProductIn, OrderStatus
from nprOlusolaBe.lib.database.base_model import BaseModel
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.utils.random_string import generate_orderId


class Order(BaseModel):
    user: User = edgy.ForeignKey("User", on_delete=edgy.CASCADE)
    order_items: list[OrderProductIn] = edgy.JSONField()
    orderId: str = edgy.CharField(max_length=20, default=lambda: generate_orderId(10))
    status: OrderStatus = edgy.ChoiceField(
        choices=OrderStatus,
        default=OrderStatus.PENDING,
    )


