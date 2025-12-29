import edgy

from nprOlusolaBe.lib.database.base_model import BaseModel


class Contact(BaseModel):
    name: str = edgy.CharField(max_length=40)
    company: str = edgy.CharField(max_length=100)
    email: str = edgy.EmailField(max_length=120, unique=True)
    content: str = edgy.TextField()
