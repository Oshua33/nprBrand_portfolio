from datetime import datetime
import edgy
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.lib.database.base_model import BaseModel


class Event(BaseModel):
    title: str = edgy.CharField(max_length=100)
    content: str = edgy.TextField(null=True)
    image: Media = edgy.ForeignKey(Media, on_delete=edgy.SET_NULL, null=True)
    start_time: datetime = edgy.TimeField()
    end_time: datetime = edgy.TimeField()
    start_date: datetime = edgy.DateTimeField()
    end_date: datetime = edgy.DateTimeField()
    url: str | None = edgy.URLField(max_length=2005, null=True)
    location: str = edgy.CharField(max_length=100)
    is_active: bool = edgy.BooleanField(default=True)
