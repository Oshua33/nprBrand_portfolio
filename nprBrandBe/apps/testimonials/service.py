import uuid
from edgy import Q, or_
from nprOlusolaBe.apps.testimonials.models import Testimonial
from nprOlusolaBe.core.schema import QueryType, QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.media.service import MediaService
from nprOlusolaBe.apps.testimonials.v1 import schemas


class TestimonialService:
    _service = BaseService[Testimonial](model=Testimonial, model_name="Testimonial")
    _media_service = MediaService()

    async def create(self, payload: schemas.TestimonialIn):
        media_instance = await self._media_service.get_file(file_id=payload.image_id)

        # Prepare payload with the fetched Media instance
        testimonial_data = payload.model_dump()
        testimonial_data["image"] = media_instance

        return await self._service.get_or_create(
            payload=testimonial_data,
            check={"name": payload.name, "content": payload.content},
            raise_error=True,
        )

    async def get(
        self,
        testimonial_id: uuid.UUID,
        load_related: bool = False,
        is_active: bool = None,
    ):
        check = {}
        if is_active is not None:
            check["is_active"] = is_active

        return await self._service.get_single(
            object_id=testimonial_id,
            load_related=load_related,
            check=check,
        )

    async def get_all(self, params: QueryType):
        check_list = []
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    name__icontains=params.filter_string,
                    content__icontains=params.filter_string,
                )
            )

        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check_list=check_list,
            fetch_distinct=True,
        )
        return result

    async def delete(self, testimonial_id: uuid.UUID):
        return await self._service.delete(id=testimonial_id)

    async def update(
        self,
        testimonial_id: uuid.UUID,
        payload: schemas.TestimonialIn,
    ) -> Testimonial:

        await self._service.get(id=testimonial_id, raise_error=True)
        check = await self._service.filter_obj(
            get_first=True,
            check={"name": payload.name, "content": payload.content},
            raise_error=False,
        )
        return await self._service.update(id=testimonial_id, payload=payload)
