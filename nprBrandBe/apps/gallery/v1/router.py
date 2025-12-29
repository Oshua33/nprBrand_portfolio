from uuid import UUID
from esmerald import Stream
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.gallery.models import Gallery
from nprOlusolaBe.apps.gallery.service import GalleryService
from nprOlusolaBe.core.schema import GetSingleParams, IFilterList, IFilterSingle
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    QueryType,
    response,
    single_details_params,
)
from nprOlusolaBe.apps.gallery.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware

class GalleryAPIView(APIView):
    path = "/galleries"
    tags = ["Gallery management"]
    dependencies = {"service": Inject(GalleryService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware],
    )
    async def create(
        self,
        payload: schemas.GalleryIn,
        service: GalleryService = Injects(),
    ) -> Gallery:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params)})
    async def list_medias(
        self,
        params: QueryType = Injects(),
        service: GalleryService = Injects(),
    ) -> IFilterList | list[Gallery] | Stream:
        return await service.get_all(params=params)

    @get(
        "/{gallery_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_media_details(
        self,
        gallery_id: UUID,
        params: GetSingleParams = Injects(),
        service: GalleryService = Injects(),
    ) -> IFilterSingle:
        return await service.get(gallery_id=gallery_id, params=params)

    @put("/{gallery_id}", responses=response)
    async def update_media_details(
        self,
        gallery_id: UUID,
        payload: schemas.GalleryIn,
        service: GalleryService = Injects(),
    ) -> Gallery:
        return await service.update(gallery_id=gallery_id, payload=payload)

    @delete(
        "/{gallery_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware],
    )
    async def delete_media(
        self,
        gallery_id: UUID,
        service: GalleryService = Injects(),
    ) -> Gallery:
        return await service.delete(gallery_id=gallery_id)
