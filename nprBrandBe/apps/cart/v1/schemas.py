import uuid
from pydantic import BaseModel


class CartIn(BaseModel):
    user_id: uuid.UUID
    quantity: int
    product_id: uuid.UUID
    
