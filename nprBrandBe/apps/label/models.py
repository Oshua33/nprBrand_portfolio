import edgy
from nprOlusolaBe.lib.database.base_model import BaseModel


class Label(BaseModel):
    title: str = edgy.CharField(max_length=100)
    type: str = edgy.CharField(max_length=20)
