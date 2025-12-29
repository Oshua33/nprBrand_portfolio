import edgy
from nprOlusolaBe.apps.label.models import Label
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.lib.database.base_model import BaseModel


class Gallery(BaseModel):
    title: str = edgy.CharField(max_length=100)
    label: Label = edgy.ForeignKey(Label, related_name="labels")
    image: Media = edgy.ForeignKey(Media, on_delete=edgy.SET_NULL, null=True)
    
