from uuid import UUID

from esmerald import Request
from nprOlusolaBe.apps.account.models import User


def get_owner_view_id(User: User, field_name: str = "id") -> UUID:
    return getattr(User, field_name)


def get_owner_view_id_from_request(
    request: Request,
    field_name: str = "id",
) -> UUID:
    user = request.user
    return getattr(user, field_name)
