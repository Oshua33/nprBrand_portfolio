from pydantic import BaseModel, EmailStr


class NewsLetterIn(BaseModel):
    email: EmailStr
