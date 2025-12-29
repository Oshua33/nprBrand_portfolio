from uuid import UUID
from esmerald import Stream
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.news_letter.models import NewsLetter
from nprOlusolaBe.apps.news_letter.service import NewsLetterService
from nprOlusolaBe.core.schema import IFilterList, QueryTypeWithoutLoadRelated
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    response,
)
from nprOlusolaBe.apps.news_letter.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin


class NewsLetterAPIView(APIView):
    path = "/newsletter"
    tags = ["News letter management"]
    dependencies = {"service": Inject(NewsLetterService)}

    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create(
        self,
        payload: schemas.NewsLetterIn,
        service: NewsLetterService = Injects(),
    ) -> NewsLetter:
        return await service.create(payload=payload)

    @get(
        "/",
        dependencies={"params": Inject(query_params_without_load_related)})
    async def list_new_letters(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: NewsLetterService = Injects(),
    ) -> IFilterList | list[NewsLetter] | Stream:
        return await service.get_all(params=params)

    @get(
        "/{news_letter_id}",
        responses=response)
    async def get_new_letter_details(
        self,
        news_letter_id: UUID,
        service: NewsLetterService = Injects(),
    ) -> NewsLetter:
        return await service.get(news_letter_id=news_letter_id)

    @put(
        "/{news_letter_id}",
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def update_new_letter_details(
        self,
        news_letter_id: UUID,
        payload: schemas.NewsLetterIn,
        service: NewsLetterService = Injects(),
    ) -> NewsLetter:
        return await service.update(news_letter_id=news_letter_id, payload=payload)

    @delete(
        "/{news_letter_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin],
    )
    async def delete_new_letter(
        self,
        news_letter_id: UUID,
        service: NewsLetterService = Injects(),
    ) -> NewsLetter:
        return await service.delete(news_letter_id=news_letter_id)
