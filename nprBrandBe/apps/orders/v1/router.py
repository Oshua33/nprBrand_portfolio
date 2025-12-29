from uuid import UUID
from esmerald import APIView, Request, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.core.schema import GetSingleParams, IFilterList, IFilterSingle
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    QueryTypeWithoutLoadRelated,
    response,
    single_details_params,
)
from nprOlusolaBe.apps.orders.v1 import schemas
from nprOlusolaBe.apps.orders.service import OrderService
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request

from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin, IsCustomer

class OrderAPIView(APIView):
    path = "/orders"
    tags = ["Order management"]
    dependencies = {"service": Inject(OrderService)}
    middleware=[JWTAuthMiddleware]
    permissions=[IsCustomer, IsAdminOrSuperAdmin]
    
    
    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create(
        self,
        payload: schemas.OrderIn,
        request: Request,
        service: OrderService = Injects(),
    ) -> Order:
        return await service.add_to_order(
            user_id=get_owner_view_id_from_request(request),
            payload=payload, )

    @get(
        "/",
        dependencies={"params": Inject(query_params_without_load_related)},
        responses=response,
    )
    async def get_order_items(
        self,
        request: Request,
        params: QueryTypeWithoutLoadRelated = Injects(),
        # user_id: UUID = None,
        service: OrderService = Injects(),
    ) -> IFilterList:
        return await service.get_orders(
            user_id=get_owner_view_id_from_request(request),
            params=params)

    @get(
        "/{order_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_order_item(
        self,
        order_id: UUID,
        request: Request,
        params: GetSingleParams = Injects(),
        service: OrderService = Injects(),
    ) -> IFilterSingle:
        return await service.get_order(
            user_id=get_owner_view_id_from_request(request),
            params=params,
            order_id=order_id,
        )

    @put("/{order_id}/items", responses=response)
    async def update_order_item_status(
        self,
        request: Request,
        order_id: UUID,
        payload: schemas.UpdateOrderItemStatus,
        service: OrderService = Injects(),
    ) -> Order:
        return await service.update_order_item_status(
            user_id=get_owner_view_id_from_request(request),
            payload=payload,
            order_id=order_id
        )
        
        # middlewares
    @put("/{order_id}", responses=response,)
    async def update_order_status(
        self,
        request: Request,
        order_id: UUID,
        payload: schemas.UpdateOrder,
        service: OrderService = Injects(),
    ) -> Order:
        return await service.update_order_status(
            user_id=get_owner_view_id_from_request(request),
            payload=payload,
            order_id=order_id
        )

    @delete("/{order_id}", status_code=status.HTTP_200_OK, responses=response)
    async def remove_order_item(
        self,
        order_id: UUID,
        request: Request,
        service: OrderService = Injects(),
    ) -> Order:
        return await service.remove_order_item(
            user_id=get_owner_view_id_from_request(request),
            order_id=order_id,
        )
