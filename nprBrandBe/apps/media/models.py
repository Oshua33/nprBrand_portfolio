import edgy
from nprOlusolaBe.lib.database.base_model import BaseModel


class Media(BaseModel):
    url: str = edgy.URLField(max_length=400)
    type: str = edgy.CharField(max_length=50)
    file_name: str = edgy.CharField(max_length=150, unique=True)
    is_active: bool = edgy.BooleanField(default=False)
