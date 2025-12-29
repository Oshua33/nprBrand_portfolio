from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from uuid import UUID
from esmerald import Stream
from esmerald import APIView, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.label.models import Label
from nprOlusolaBe.apps.label.service import LabelService
from nprOlusolaBe.core.schema import (
    IFilterList,
    QueryTypeWithoutLoadRelated,
)
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    response,
)
from nprOlusolaBe.apps.label.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin


class LabelAPIView(APIView):
    path = "/labels"
    tags = ["labels management"]
    dependencies = {"service": Inject(LabelService)}
    middleware = [JWTAuthMiddleware]
    permissions = [IsAdminOrSuperAdmin]

    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create_label(
        self,
        payload: schemas.LabelIn,
        service: LabelService = Injects(),
    ) -> Label:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params_without_load_related)})
    async def list_labels(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: LabelService = Injects(),
    ) -> IFilterList | list[Label] | Stream:
        return await service.get_all(params=params)

    @get("/{label_id}", responses=response)
    async def get_label_details(
        self,
        label_id: UUID,
        service: LabelService = Injects(),
    ) -> Label:
        return await service.get(label_id=label_id)

    @put("/{label_id}", responses=response)
    async def update_label_details(
        self,
        label_id: UUID,
        payload: schemas.LabelIn,
        service: LabelService = Injects(),
    ) -> Label:
        return await service.update(label_id=label_id, payload=payload)

    @delete("/{label_id}", status_code=status.HTTP_200_OK, responses=response)
    async def delete_label(
        self,
        label_id: UUID,
        service: LabelService = Injects(),
    ) -> Label:
        return await service.delete(label_id=label_id)
