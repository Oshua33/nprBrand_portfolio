from pydantic import BaseModel, Field


class LabelIn(BaseModel):
    title: str = Field(max_length=100)
    type: str = Field(max_length=20)
