from uuid import UUID
from esmerald import Stream
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.testimonials.models import Testimonial
from nprOlusolaBe.apps.testimonials.service import TestimonialService
from nprOlusolaBe.core.schema import IFilterList
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    QueryType,
    response,
)
from nprOlusolaBe.apps.testimonials.v1 import schemas



class TestimonialAPIView(APIView):
    path = "/testimonials"
    tags = ["Testimonials management"]
    dependencies = {"service": Inject(TestimonialService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def create_testimonial(
        self,
        payload: schemas.TestimonialIn,
        service: TestimonialService = Injects(),
    ) -> Testimonial:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params)})
    async def list_testimonials(
        self,
        params: QueryType = Injects(),
        service: TestimonialService = Injects(),
    ) -> IFilterList | list[Testimonial] | Stream:
        return await service.get_all(params=params)

    @get("/{testimonial_id}", responses=response)
    async def get_testimonial_details(
        self,
        testimonial_id: UUID,
        service: TestimonialService = Injects(),
        load_related: bool = False,
        is_active: bool = False,
    ) -> Testimonial:
        return await service.get(
            testimonial_id=testimonial_id,
            is_active=is_active,
            load_related=load_related,
        )

    @put(
        "/{testimonial_id}",
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def update_testimonial_details(
        self,
        testimonial_id: UUID,
        payload: schemas.TestimonialIn,
        service: TestimonialService = Injects(),
    ) -> Testimonial:
        return await service.update(testimonial_id=testimonial_id, payload=payload)

    @delete(
        "/{testimonial_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def delete_testimonial(
        self,
        testimonial_id: UUID,
        service: TestimonialService = Injects(),
    ) -> Testimonial:
        return await service.delete(testimonial_id=testimonial_id)
