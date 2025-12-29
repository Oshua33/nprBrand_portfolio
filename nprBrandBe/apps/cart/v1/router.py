from uuid import UUID
from esmerald import APIView, Request, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.core.schema import GetSingleParams, IFilterList, IFilterSingle
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    QueryTypeWithoutLoadRelated,
    response,
    single_details_params,
)
from nprOlusolaBe.apps.cart.v1 import schemas
from nprOlusolaBe.apps.cart.service import CartService
from nprOlusolaBe.apps.cart.models import Cart, Cart
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin, IsCustomer
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request

class CartAPIView(APIView):
    path = "/carts"
    tags = ["Cart management"]
    dependencies = {"service": Inject(CartService)}
    middleware = [JWTAuthMiddleware]
    permissions =[IsCustomer, IsAdminOrSuperAdmin]

    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create(
        self,
        payload: schemas.CartIn,
        request: Request,
        service: CartService = Injects(),
    ) -> Cart:
        return await service.add_to_cart(payload=payload, 
                                        user_id=get_owner_view_id_from_request(request))

    @get(
        "/",
        dependencies={"params": Inject(query_params_without_load_related)},
        responses=response,
    )
    async def get_cart_items(
        self,
        request: Request,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: CartService = Injects(),
    ) -> IFilterList:
        return await service.get_carts(params=params, user_id=get_owner_view_id_from_request(request))

    @get(
        "/{cart_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_cart_item(
        self,
        cart_id: UUID,
        request: Request,
        params: GetSingleParams = Injects(),
        service: CartService = Injects(),
    ) -> IFilterSingle:
        return await service.get_cart(
            params=params,
            user_id=get_owner_view_id_from_request(request),
            cart_id=cart_id)

    @put("/{cart_id}/", responses=response)
    async def update_cart_item(
        self,
        cart_id: UUID,
        request: Request,
        payload: schemas.CartIn,
        service: CartService = Injects(),
    ) -> Cart:
        return await service.update_cart(
            cart_id=cart_id,
            payload=payload,
            user_id=get_owner_view_id_from_request(request))

    @delete("/{cart_id}", status_code=status.HTTP_200_OK, responses=response)
    async def remove_cart_item(
        self,
        cart_item: UUID,
        request: Request,
        service: CartService = Injects(),
    ) -> Cart:
        return await service.remove_cart_item(cart_item=cart_item, user_id=get_owner_view_id_from_request(request))