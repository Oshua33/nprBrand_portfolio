import uuid
from edgy import or_
from nprOlusolaBe.apps.label.models import Label
from nprOlusolaBe.core.schema import QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.label.v1 import schemas


class LabelService:
    _service = BaseService[Label](model=Label, model_name="Label")

    async def create(self, payload: schemas.LabelIn):
        return await self._service.get_or_create(
            payload=payload,
            check={"title": payload.title},
            raise_error=True,
        )

    async def get(self, label_id: uuid.UUID):
        return await self._service.get(id=label_id)

    async def get_all(self, params: QueryTypeWithoutLoadRelated):
        check_list = []
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(title__icontains=params.filter_string),
            )
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check_list=check_list,
            fetch_distinct=True,
        )
        return result

    async def delete(self, label_id: uuid.UUID):
        return await self._service.delete(id=label_id)

    async def update(self, label_id: uuid.UUID, payload: schemas.LabelIn):
        check = await self._service.filter_obj(
            get_first=True,
            check={"title": payload.title},
            raise_error=False,
        )
        if check and check.id != label_id:
            raise ValueError(
                f"A {self._service.model_name} with this title {payload.title} already exist"
            )
        return await self._service.update(
            id=label_id,
            payload=payload,
        )
