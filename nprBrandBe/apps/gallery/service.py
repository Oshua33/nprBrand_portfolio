import uuid
from edgy import or_
from nprOlusolaBe.apps.gallery.models import Gallery
from nprOlusolaBe.core.schema import GetSingleParams, QueryType
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.media.service import MediaService
from nprOlusolaBe.apps.label.service import LabelService
from nprOlusolaBe.apps.gallery.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response


class GalleryService:
    _service = BaseService[Gallery](model=Gallery, model_name="gallery")
    _media_service = MediaService()
    _label_service = LabelService()

    async def create(self, payload: schemas.GalleryIn):
        media_instance = await self._media_service.get_file(file_id=payload.image_id)
        label_instance = await self._label_service.get(label_id=payload.label_id)

        # Prepare payload with the fetched Media instance
        gallery_data = payload.model_dump()
        gallery_data["image"] = media_instance
        gallery_data["label"] = label_instance

        return await self._service.get_or_create(
            payload=gallery_data,
            check={"title": payload.title},
            raise_error=False,
        )

    async def get(self, gallery_id: uuid.UUID, params: GetSingleParams = None):
        return await self._service.get_single(
            object_id=gallery_id,
            **params.model_dump(),
        )

    async def get_all(self, params: QueryType):
        check_list = []
        if params.filter_string:
            check_list.append(or_.from_kwargs(title__icontains=params.filter_string))
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check_list=check_list,
            fetch_distinct=True,
        )
        return result

    async def delete(self, gallery_id: uuid.UUID):
        return await self._service.delete(id=gallery_id)

    async def update(
        self,
        gallery_id: uuid.UUID,
        payload: schemas.GalleryIn,
    ) -> Gallery:
        await self._service.get(id=gallery_id, raise_error=True)
        check = await self._service.filter_obj(
            get_first=True,
            check={"title": payload.title},
            raise_error=False,
        )
        if check and check.id != gallery_id:
            raise get_error_response(
                f"A {self._service.model_name} with this title {payload.title} already exist",
            )
        return await self._service.update(id=gallery_id, payload=payload)
