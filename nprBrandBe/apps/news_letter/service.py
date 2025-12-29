import uuid
from edgy import or_
from nprOlusolaBe.apps.news_letter.models import NewsLetter
from nprOlusolaBe.core.schema import QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.news_letter.v1 import schemas


class NewsLetterService:
    _service = BaseService[NewsLetter](model=NewsLetter, model_name="News Letter")

    async def create(self, payload: schemas.NewsLetterIn):
        return await self._service.get_or_create(
            payload=payload,
            check={"email": payload.email},
            raise_error=False,
        )

    async def get(self, news_letter_id: uuid.UUID):
        return await self._service.get(id=news_letter_id)

    async def get_all(self, params: QueryTypeWithoutLoadRelated):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(or_.from_kwargs(email__icontains=params.filter_string))
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )
        return result

    async def delete(self, news_letter_id: uuid.UUID):
        return await self._service.delete(id=news_letter_id)

    async def update(self, news_letter_id: uuid.UUID, payload: schemas.NewsLetterIn):
        check = await self._service.filter_obj(
            get_first=True,
            check={"email": payload.email},
            raise_error=False,
        )
        if check and check.id != news_letter_id:
            raise ValueError(
                f"A {self._service.model_name} with this email {payload.email} already exist"
            )
        return await self._service.update(id=news_letter_id, payload=payload)
