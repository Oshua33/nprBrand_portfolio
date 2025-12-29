from typing import Optional
from uuid import UUID
from esmerald import Stream
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from h11 import Request
from nprOlusolaBe.apps.reviews.models import Review
from nprOlusolaBe.apps.reviews.service import ReviewService
from nprOlusolaBe.core.schema import IFilterList, QueryType
from nprOlusolaBe.core.schema import IFilterList
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request
from nprOlusolaBe.utils.list_endpoint_query_params import query_params, response
from nprOlusolaBe.apps.reviews.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin, IsCustomer


class ReviewAPIView(APIView):
    path = "/reviews"
    tags = ["Review management"]
    dependencies = {"service": Inject(ReviewService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
    )
    async def create(
        self,
        request: Request,
        payload: schemas.ReviewIn,
        service: ReviewService = Injects(),
    ) -> Review:
        return await service.create(
            payload=payload,
            reviewer_id=get_owner_view_id_from_request(request=request),
        )

    @get("/", dependencies={"params": Inject(query_params)})
    async def list_reviews(
        self,
        params: QueryType = Injects(),
        is_accepted: Optional[bool] = None,
        service: ReviewService = Injects(),
    ) -> IFilterList | list[Review] | Stream:
        return await service.get_all(params=params, is_accepted=is_accepted)

    @get("/{review_id}", responses=response)
    async def get_review_details(
        self,
        review_id: UUID,
        service: ReviewService = Injects(),
    ) -> Review:
        return await service.get(review_id=review_id)

    @put(
        "/{review_id}",
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
    )
    async def update_review_details(
        self,
        review_id: UUID,
        request: Request,
        payload: schemas.ReviewIn,
        service: ReviewService = Injects(),
    ) -> Review:
        return await service.update(
            review_id=review_id,
            payload=payload,
            reviewer_id=get_owner_view_id_from_request(request=request),
        )

    @put(
        "/{review_id}",
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def update_review_status(
        self,
        review_id: UUID,
        payload: schemas.ReviewUpdateStatusIn,
        service: ReviewService = Injects(),
    ) -> Review:
        return await service.update(review_id=review_id, payload=payload)

    @delete(
        "/{review_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def delete_review(
        self,
        review_id: UUID,
        service: ReviewService = Injects(),
    ) -> Review:
        return await service.delete(review_id=review_id)
