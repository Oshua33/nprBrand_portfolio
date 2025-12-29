from pydantic import BaseModel, Field, EmailStr


class ContactIn(BaseModel):
    name: str = Field(max_length=40)
    company: str = Field(max_length=100)
    email: EmailStr
    content: str 
