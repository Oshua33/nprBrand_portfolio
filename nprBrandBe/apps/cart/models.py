import uuid
import edgy
from nprOlusolaBe.lib.database.base_model import BaseModel
from nprOlusolaBe.apps.product.models import Product
from nprOlusolaBe.apps.account.models import User


class Cart(BaseModel):
    user: User | None = edgy.ForeignKey("User", on_delete=edgy.CASCADE)
    product: Product = edgy.ForeignKey("Product", on_delete=edgy.CASCADE)
    quantity: int = edgy.IntegerField(default=1)
