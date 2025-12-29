import uuid
from pydantic import BaseModel, Field
from typing import Optional


class BlogIn(BaseModel):
    title: str = Field(max_length=40)
    description: str
    label_id: Optional[uuid.UUID]
    category_id: Optional[uuid.UUID]
    image_id: Optional[uuid.UUID] = None
    is_publish: bool = False


class BlogCategoryIn(BaseModel):
    name: str


class BlogCategoryUpdate(BlogCategoryIn):
    pass


class BlogTagIn(BaseModel):
    name: str


class BlogLikeIn(BaseModel):
    blog_id: uuid.UUID


class BlogCommentIn(BaseModel):
    blog_id: str
    comment: str
