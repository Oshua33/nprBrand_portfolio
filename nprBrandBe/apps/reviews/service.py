from typing import Optional
import uuid
from edgy import or_
from nprOlusolaBe.apps.reviews.models import Review
from nprOlusolaBe.core.schema import QueryType
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.reviews.v1 import schemas


class ReviewService:
    _service = BaseService[Review](model=Review, model_name="Review")

    async def create(
        self,
        payload: schemas.ReviewIn,
        reviewer_id: uuid.UUID,
    ):
        return await self._service.get_or_create(
            payload=payload,
            check={
                "name": payload.name,
                "content": payload.content,
                "email": payload.email,
                "reviewer_id": reviewer_id,
            },
            raise_error=False,
        )

    async def get(self, review_id: uuid.UUID):
        return await self._service.get(id=review_id)

    async def get_all(self, params: QueryType, is_accepted: Optional[bool] = None):
        check_list = []
        check = {}
        if is_accepted is not None:
            check["is_accepted"] = is_accepted
        if params.filter_string:
            check_list.append(
                or_(
                    name__icontains=params.filter_string,
                    email__icontains=params.filter_string,
                    content__icontains=params.filter_string,
                )
            )
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check_list=check_list,
            check=check,
            fetch_distinct=True,
        )
        return result

    async def delete(self, review_id: uuid.UUID):
        return await self._service.delete(id=review_id)

    async def update(
        self,
        review_id: uuid.UUID,
        payload: schemas.ReviewIn | schemas.ReviewUpdateStatusIn,
        reviewer_id: uuid.UUID,
    ) -> Review:
        return await self._service.update(
            id=review_id,
            payload=payload,
            check={"reviewer_id": reviewer_id},
        )

    async def update_status(
        self,
        review_id: uuid.UUID,
        payload: schemas.ReviewUpdateStatusIn,
    ) -> Review:
        return await self._service.update(
            id=review_id,
            payload=payload,
        )
