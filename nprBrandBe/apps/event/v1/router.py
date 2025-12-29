from typing import List
from uuid import UUID
from esmerald import Stream
from esmerald.responses import StreamingResponse
from esmerald import APIView, Query, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.event.models import Event
from nprOlusolaBe.apps.event.service import EventService
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    IFilterList,
    IFilterSingle,
    QueryType,
)
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    response,
    single_details_params,
)
from nprOlusolaBe.apps.event.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware


class EventAPIView(APIView):
    path = "/events"
    tags = ["Event management"]
    dependencies = {"service": Inject(EventService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def create(
        self,
        payload: schemas.EventIn,
        service: EventService = Injects(),
    ) -> Event:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params)})
    async def list_event(
        self,
        params: QueryType = Injects(),
        service: EventService = Injects(),
        is_active: bool | None = Query(default=None),
    ) -> IFilterList | List[Event] | StreamingResponse:
        return await service.get_all(
            params=params,
            is_active=is_active,
        )

    @get(
        "/{event_id}",
        responses=response,
        dependencies={"params": Inject(single_details_params)},
    )
    async def get_event_details(
        self,
        event_id: UUID,
        params: GetSingleParams = Injects(),
        is_active: bool | None = Query(default=None),
        service: EventService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            event_id=event_id,
            is_active=is_active,
            params=params,
        )

    @put(
        "/{event_id}",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def update_event_details(
        self,
        event_id: UUID,
        payload: schemas.EventIn,
        service: EventService = Injects(),
    ) -> Event:
        return await service.update(event_id=event_id, payload=payload)

    @delete(
        "/{event_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def delete_event(
        self,
        event_id: UUID,
        service: EventService = Injects(),
    ) -> Event:
        return await service.delete(event_id=event_id)
