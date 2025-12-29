import edgy
from nprOlusolaBe.lib.database.base_model import BaseModel


class NewsLetter(BaseModel):
    email: str = edgy.EmailField(max_length=40)
