import uuid
from pydantic import BaseModel, Field


class GalleryIn(BaseModel):
    title: str = Field(max_length=100)
    label_id: uuid.UUID
    image_id: uuid.UUID
