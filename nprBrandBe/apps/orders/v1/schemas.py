from decimal import Decimal
from enum import Enum
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class OrderProductStatus(Enum):
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"


class OrderStatus(Enum):
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"
    READY_FOR_SHIPMENT = "ready for shipment"
    SHIPPED = "shipped"


class OrderProductIn(BaseModel):
    id: uuid.UUID
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    image_url: str
    quantity: int
    status: Optional[OrderProductStatus] = None


class OrdersItem(BaseModel):
    product_id: str
    quantity: int
    price: Decimal = Field(max_digits=10, decimal_places=2)


class UpdateOrder(BaseModel):
    status: OrderStatus


class RemoveProductFromOrder(BaseModel):
    product_ids: list[uuid.UUID]


class UpdateOrderItemStatus(BaseModel):
    product_id: uuid.UUID
    status: OrderProductStatus


class OrderIn(BaseModel):
    product_ids: list[uuid.UUID]
