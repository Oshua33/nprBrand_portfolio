import uuid
from esmerald import status
from edgy import Q
from nprOlusolaBe.apps.cart.models import Cart
from nprOlusolaBe.apps.cart.v1 import schemas
from nprOlusolaBe.core.schema import GetSingleParams, QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.product.service import ProductService
from nprOlusolaBe.apps.product.models import ProductStatus, Product
from nprOlusolaBe.utils.base_response import get_error_response


class CartService:
    _service = BaseService[Cart](model=Cart, model_name="Carts")
    _product_services = ProductService()

    async def add_to_cart(
        self,
        payload: schemas.CartIn,
        user_id: uuid.UUID,
    ) -> Cart:
        product: Product = await self._product_services.get(
            product_id=payload.product_id, is_trash=False
        )
        if product.status == ProductStatus.OUT_OF_STOCK:
            raise get_error_response(
                f"{self._product_services.__service.model_name} {product.name} is out of stock",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return await self._service.get_or_create(
            payload=dict(
                product_id=payload.product_id,
                quantity=payload.quantity,
                user_id=user_id,
            ),
            raise_error=True,
            check={"product_id": payload.product_id, "user_id": user_id},
        )

    async def remove_cart_item(
        self,
        cart_id: uuid.UUID,
        user_id: uuid.UUID,
    ):
        """Remove a cart item from the cart."""
        await self._service.filter_obj(
            get_first=True,
            check=dict(id=cart_id, user_id=user_id),
            raise_error=True,
        )
        return await self._service.delete(
            id=cart_id,
            check=dict(user_id=user_id),
        )

    async def update_cart(
        self,
        payload: schemas.CartIn,
        cart_id: uuid.UUID,
        user_id: uuid.UUID = None,
    ):
        """update a from the cart."""
        check = {}
        if user_id:
            check["user_id"] = user_id
        check_item = await self._service.filter_obj(
            get_first=True,
            check=dict(
                product_id=payload.product_id,
                id=cart_id,
                **check,
            ),
            raise_error=True,
        )
        product: Product = await check_item.product.load()
        if payload.quantity > product.quantity and product.quantity > 0:
            raise get_error_response(
                f" only {product.quantity} of {self._product_services._service.model_name} is left",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if payload.quantity > product.quantity and not product.quantity > 0:
            raise get_error_response(
                f"{product.name} is out of stock",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return await self._service.update(
            id=cart_id, check=check, payload=dict(quantity=payload.quantity)
        )

    async def get_carts(
        self,
        params: QueryTypeWithoutLoadRelated,
        user_id: uuid.UUID = None,
    ):
        """Retrieve all cart items for a specific user."""
        check_list = []
        check = {}
        if params.filter_string:
            check_list.append(
                Q.from_kwargs(product__name__icontains=params.filter_string)
            )
        if user_id:
            check["user_id"] = user_id
        return await self._service.filter_and_list(
            check=check,
            **params.model_dump(exclude={"filter_string"}),
        )

    async def get_cart(
        self,
        cart_id: uuid.UUID,
        params: GetSingleParams,
        user_id: uuid.UUID = None,
    ):
        """Retrieve all cart items for a specific user."""
        check = {}
        if user_id:
            check["user_id"] = user_id
        return await self._service.get_single(
            object_id=cart_id,
            check=check,
            **params.model_dump(),
        )
