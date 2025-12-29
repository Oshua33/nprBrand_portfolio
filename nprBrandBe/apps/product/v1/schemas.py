from enum import Enum
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional


class ProductStatus(Enum):
    IN_STOCK = "in stock"
    OUT_OF_STOCK = "out of stock"
    LIMITED_STOCK = "limited stock"


class ProductMetaData(BaseModel):
    key: str = Field(max_length=40)
    value: str


class ExternalProductLink(BaseModel):
    name: str = Field(max_length=40)
    link: str = Field(max_length=200)


class ProductIn(BaseModel):
    name: str = Field(max_length=40)
    content: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    image_id: Optional[uuid.UUID] = None
    quantity: int
    status: ProductStatus = ProductStatus.LIMITED_STOCK
    meta_data: Optional[list[ProductMetaData]] = []
    external_links: list[Optional[ExternalProductLink]] = []
    category_id: Optional[uuid.UUID]


class ProductAvailable(BaseModel):
    quantity: int


class ProductCategoryIn(BaseModel):
    name: str
