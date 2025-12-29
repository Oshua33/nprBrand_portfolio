from uuid import UUID
from esmerald import (
    APIView,
    Body,
    JSONResponse,
    delete,
    get,
    Inject,
    Injects,
    post,
    put,
    status,
    UploadFile,
)
from esmerald.enums import EncodingType, MediaType
from nprOlusolaBe.apps.media.models import Media
from nprOlusolaBe.apps.media.service import MediaService
from nprOlusolaBe.core.schema import IFilterList, QueryTypeWithoutLoadRelated
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    response,
)
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin


class MediaAPIView(APIView):
    path = "/s3"
    tags = ["Media management"]
    dependencies = {"service": Inject(MediaService)}
    middleware = [JWTAuthMiddleware]
    permissions = [IsAdminOrSuperAdmin]

    @post("/", responses=response, status_code=status.HTTP_201_CREATED)
    async def upload(
        self,
        data: UploadFile = Body(media_type=EncodingType.MULTI_PART),
        service: MediaService = Injects(),
    ) -> Media:
        return await service.create(data)

    @post("/bulk", responses=response, status_code=status.HTTP_201_CREATED)
    async def upload_bulk(
        self,
        data: list[UploadFile] = Body(media_type=EncodingType.MULTI_PART),
        service: MediaService = Injects(),
    ) -> JSONResponse:
        return await service.create_bulk(data)

    @put("/{file_id}", responses=response, status_code=status.HTTP_200_OK)
    async def update_file(
        self,
        file_id: UUID,
        data: UploadFile = Body(media_type=EncodingType.MULTI_PART),
        service: MediaService = Injects(),
    ) -> Media:
        return await service.update_file(file_id, data)

    @get("/{file_id}", responses=response, status_code=status.HTTP_200_OK)
    async def get_file(
        self,
        file_id: UUID,
        service: MediaService = Injects(),
    ) -> Media:
        return await service.get_file(file_id)

    @get(
        "/",
        responses=response,
        dependencies={"params": Inject(query_params_without_load_related)},
        status_code=status.HTTP_200_OK,
    )
    async def get_file_list(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: MediaService = Injects(),
    ) -> IFilterList:
        return await service.list_file(params=params)

    @delete("/{file_id}", responses=response, status_code=status.HTTP_200_OK)
    async def delete_file(
        self, file_id: UUID, service: MediaService = Injects()
    ) -> Media:
        return await service.delete_file(file_id)
