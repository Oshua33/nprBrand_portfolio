import uuid
from edgy import or_
from nprOlusolaBe.core.schema import GetSingleParams, QueryType
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.event.models import Event
from nprOlusolaBe.apps.media.service import MediaService
from nprOlusolaBe.apps.event.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response


class EventService:
    _service = BaseService[Event](model=Event, model_name="Event")
    _media_service = MediaService()

    async def create(self, payload: schemas.EventIn) -> Event:
        media_instance = await self._media_service.get_file(file_id=payload.image_id)

        # Prepare payload with the fetched Media instance
        event_data = payload.model_dump()
        event_data["image"] = media_instance

        return await self._service.get_or_create(
            payload=event_data,
            check={"title": payload.title},
            raise_error=True,
        )

    async def get(
        self,
        event_id: uuid.UUID,
        params: GetSingleParams = GetSingleParams(load_related=False),
        is_active: bool | None = None,
    ):
        check = {}
        if is_active is not None:
            check["is_active"] = is_active
        return await self._service.get_single(
            object_id=event_id,
            check=check,
            raise_error=True,
            load_related=params.load_related,
        )

    async def get_all(
        self,
        params: QueryType,
        is_active: bool | None = None,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    title__icontains=params.filter_string,
                    content__icontains=params.filter_string,
                    location__icontains=params.filter_string,
                )
            )
        if is_active is not None:
            checks["is_active"] = is_active
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
            exclude_secrets=True,
        )

    async def delete(self, event_id: uuid.UUID):
        return await self._service.delete(id=event_id)

    # does this not need to validate if the image exist and its not optional fields
    async def update(self, event_id: uuid.UUID, payload: schemas.EventIn):
        await self._service.get(id=event_id, raise_error=True)
        check = await self._service.filter_obj(
            get_first=True,
            check={"title": payload.title},
            raise_error=False,
        )
        if check and check.id != event_id:
            raise get_error_response(
                f"A {self._service.model_name} with this name {payload.title} already exist",
            )

        return await self._service.update(id=event_id, payload=payload)
