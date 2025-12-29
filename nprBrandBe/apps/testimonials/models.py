import edgy
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.lib.database.base_model import BaseModel


class Testimonial(BaseModel):
    name: str = edgy.CharField(max_length=100)
    image: Media = edgy.ForeignKey(Media, null=True, on_delete=edgy.SET_NULL)
    content: str = edgy.TextField()
    is_active: bool | None = edgy.BooleanField(null=True)
