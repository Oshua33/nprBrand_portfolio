import asyncio
import uuid
from esmerald import status
from edgy import and_, or_
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    QueryType,
)
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.contact.models import Contact
from nprOlusolaBe.apps.contact.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response



class ContactService:
    _service = BaseService[Contact](model=Contact, model_name="Contact")

    async def create(self, payload: schemas.ContactIn):
        return await self._service.get_or_create(
            payload=payload,
            check={"email": payload.name},
            raise_error=True,
        )

    async def get(self, contact_id: uuid.UUID):
        return await self._service.get(id=contact_id, raise_error=True)

    async def get_all(
        self,
        params: QueryType,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_(
                    name__icontains=params.filter_string,
                    email__icontains=params.filter_string,
                    company__icontains=params.filter_string,
                    content__icontains=params.filter_string,
                    
                )
            )
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )

    async def update(
        self, contact_id: uuid.UUID, payload: schemas.ContactIn
    ) -> Contact:
        check_category = await self._service.filter_obj(
            get_first=True, check={"name": payload.name}, raise_error=False
        )
        if check_category:
            raise get_error_response(
                f" A {self._service.model_name} with this name {payload.name} already exist",
                status_code=status.HTTP_409_CONFLICT,
            )
        return await self._service.update(id=contact_id, payload=payload)

    async def delete(self, contact_id: uuid.UUID):
        return await self._service.delete(id=contact_id)
