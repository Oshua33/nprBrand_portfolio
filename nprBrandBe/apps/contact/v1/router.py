from uuid import UUID
from esmerald import Stream
from esmerald import (
    APIView,
    delete,
    get,
    Inject,
    Injects,
    post,
    put,
    status,
)
from nprOlusolaBe.apps.contact.service import  ContactService
from nprOlusolaBe.apps.contact.models import Contact
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.core.schema import (
    IFilterList,
    IFilterSingle,
)
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    QueryType,
    response,
)
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request
from nprOlusolaBe.apps.contact.v1 import schemas
from nprOlusolaBe.middleware.permission import IsCustomer, IsAdminOrSuperAdmin
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware


class ContactAPIView(APIView):
    path = "/contacts"
    tags = ["Contact management"]
    dependencies = {"service": Inject(ContactService)}

    @get("/", dependencies={"params": Inject(query_params)},
         permissions=[IsAdminOrSuperAdmin],
          middleware=[JWTAuthMiddleware])
    async def get_all(
        self,
        params: QueryType = Injects(),
        service: ContactService = Injects(),
    ) -> IFilterList | list[Contact] | Stream:
        return await service.get_all(params=params)


    @get(
        "/{contact_id}",
        responses=response,
    )
    async def get_contact_details(
        self,
        contact_id: UUID,
        service: ContactService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            contact_id=contact_id
        )

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
    )
    async def create_contact(
        self,
        payload: schemas.ContactIn,
        service: ContactService = Injects(),
    ) -> Contact:
        return await service.create(payload=payload)

    @put(
        "/{contact_id}",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware]
    )
    async def update_contact(
        self,
        contact_id: UUID,
        payload: schemas.ContactIn,
        service: ContactService = Injects(),
    ) -> Contact:
        return await service.update(contact_id=contact_id, payload=payload)

    @delete(
        "/{contact_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin]
    )
    async def delete_contact(
        self, contact_id: UUID, service: ContactService = Injects()
    ) -> Contact:
        return await service.delete(contact_id=contact_id)

