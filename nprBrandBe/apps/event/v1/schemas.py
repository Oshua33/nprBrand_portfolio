import uuid
from pydantic import BaseModel, Field, field_validator
import datetime


class EventIn(BaseModel):
    title: str = Field(max_length=100)
    content: str
    image_id: uuid.UUID = None
    start_time: datetime.time = Field(default=datetime.datetime.now().time())
    end_time: datetime.time = Field(default=datetime.datetime.now().time())
    start_date: datetime.date = Field(default=datetime.date.today())
    end_date: datetime.date = Field(default=datetime.date.today())
    url: str | None = Field(default=None, max_length=2005)
    location: str = Field(default="remote", max_length=150)
    is_active: bool = False

    @field_validator("start_date")
    def validate_date(cls, v: datetime.date):
        if v < datetime.date.today():
            raise ValueError("Date cannot be in the past")
        return v
