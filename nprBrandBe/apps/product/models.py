from decimal import Decimal
import edgy
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.apps.product.v1.schemas import ExternalProductLink, ProductStatus
from nprOlusolaBe.lib.database.base_model import BaseModel
from nprOlusolaBe.apps.account.models import User

class ProductCategory(BaseModel):
    name: str = edgy.CharField(max_length=100)


class Product(BaseModel):
    name: str = edgy.CharField(max_length=100)
    content: str = edgy.TextField()
    price: Decimal = edgy.DecimalField(max_digits=10, decimal_places=2)
    image: Media = edgy.ForeignKey(Media, on_delete=edgy.SET_NULL, null=True)
    quantity: int = edgy.IntegerField(default=0)
    external_links: list[ExternalProductLink] = edgy.JSONField(default=[])
    meta_data: dict = edgy.JSONField(default=[])
    author: User | None = edgy.ForeignKey(
        "User",
        on_delete=edgy.CASCADE,
        related_name="author",
        null=True,
    )
    category: ProductCategory | None = edgy.ForeignKey(
        "ProductCategory",
        null=True,
        on_delete=edgy.SET_NULL,
    )
    is_trash: bool = edgy.BooleanField(default=False)
    status: ProductStatus = edgy.ChoiceField(
        ProductStatus, default=ProductStatus.IN_STOCK
    )
