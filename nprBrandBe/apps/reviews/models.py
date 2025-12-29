import edgy
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.lib.database.base_model import BaseModel


class Review(BaseModel):
    name: str = edgy.CharField(max_length=100)
    email: str = edgy.EmailField(max_length=40)
    content: str = edgy.TextField()
    reviewer: User = edgy.ForeignKey(
        User, related_name=None, on_delete=edgy.SET_NULL, null=True
    )
    is_accepted: bool | None = edgy.BooleanField(null=True)
