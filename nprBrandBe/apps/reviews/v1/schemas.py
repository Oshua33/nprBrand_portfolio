from pydantic import BaseModel, Field, EmailStr


class ReviewIn(BaseModel):
    name: str = Field(max_length=100)
    email: EmailStr
    content: str


class ReviewUpdateStatusIn(BaseModel):
    is_accepted: bool | None = None
