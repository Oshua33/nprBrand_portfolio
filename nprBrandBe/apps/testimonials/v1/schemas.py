import uuid
from pydantic import BaseModel, Field, AnyUrl


class TestimonialIn(BaseModel):
    name: str = Field(max_length=100)
    image_id: uuid.UUID = None
    content: str
    is_active: bool | None = False
