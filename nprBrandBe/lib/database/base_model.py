import edgy
from ulid import ULID

from nprOlusolaBe.lib.database.connection import get_db_connection


registry = get_db_connection()


class BaseModel(edgy.Model):
    id = edgy.UUIDField(primary_key=True, default=lambda: ULID().to_uuid())
    created_at = edgy.DateTimeField(auto_now_add=True)
    updated_at = edgy.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        registry = registry

