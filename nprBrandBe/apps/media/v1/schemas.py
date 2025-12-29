from pydantic import BaseModel


class MediaIn(BaseModel):
    url: str
    type: str
    file_name: str
