import uuid
from typing import Optional
import edgy
from esmerald import status
from edgy import or_
from nprOlusolaBe.apps.cart.service import CartService
from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.apps.orders.v1 import schemas
from nprOlusolaBe.core.schema import GetSingleParams, QueryTypeWithoutLoadRelated
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.product.service import ProductService
from nprOlusolaBe.apps.product.models import ProductStatus
from nprOlusolaBe.utils.base_response import get_error_response
import asyncio


class OrderService:
    def __init__(self):
        self._service = BaseService[Order](model=Order, model_name="Order")
        self.__cart_service = CartService()
        self.__product_service = ProductService()

    async def __load_related(self, items: list[edgy.Model]):
        """
            Load related products and images for the given carts.

            Args:
                carts: List of Cart instances
        Returns:
            List of Cart instances with related products and images loaded
        """
        tasks = [item.load() for item in items]
        await asyncio.gather(*tasks)

    async def add_to_order(
        self,
        payload: schemas.OrderIn,
        user_id: uuid.UUID,
    ) -> Order:
        """
        Add items to the order.

        Args:
            payload: Order input data containing product IDs and quantities
            user_id: ID of the user creating the order

        Returns:
            Created Order instance

        Raises:
            HTTPException: If there's insufficient stock
        """
        # Get all cart items in a single query
        cart_items = await self.__cart_service._service.filter_obj(
            check=dict(user_id=user_id, product__id__in=payload.product_ids),
            raise_error=True,
        )

        # Preload all products and their images in bulk
        await self.__load_related([item.product for item in cart_items])
        await self.__load_related([item.product.image for item in cart_items])

        order_items = []
        for cart_item in cart_items:
            # Check stock availability
            if cart_item.product.quantity < cart_item.quantity:
                cart_item.product.status = ProductStatus.OUT_OF_STOCK
                await cart_item.product.save()
                raise get_error_response(
                    f"Not enough stock for product {cart_item.product.name}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Prepare order item
            order_items.append(
                schemas.OrderProductIn(
                    id=cart_item.product.id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                    image_url=cart_item.product.image.url,
                    name=cart_item.product.name,
                ).model_dump()
            )

            # Update product quantity
            cart_item.product.quantity -= cart_item.quantity
            await cart_item.product.save()

        # Create order with all items
        new_order = await self._service.create(
            payload=dict(
                order_items=order_items,
                user_id=user_id,
            ),
        )
        if new_order:
            # Delete cart items associated with the order
            await self.__cart_service._service.delete_by_ids(
                object_ids=[cart_item.id in cart_items]
            )
            return new_order
        else:
            raise get_error_response(
                "Failed to create order",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def remove_order_item(
        self,
        order_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: schemas.RemoveProductFromOrder,
    ) -> Order:
        """
        Remove items from the order.

        Args:
            order_id: ID of the order
            user_id: ID of the user
            payload: Product IDs to remove

        Returns:
            Updated Order instance
        """
        order = await self._service.filter_obj(
            get_first=True,
            check=dict(id=order_id, user_id=user_id),
            raise_error=True,
        )

        # Use list comprehension to filter out removed items and update product quantities
        updated_items = []
        for item in order.order_items:
            if item.id in payload.product_ids:
                product = await self.__product_service._service.get(id=item.id)
                product.quantity += item.quantity
                await product.save()
            else:
                updated_items.append(item)

        order.order_items = updated_items
        return await order.save()

    async def update_order_item_status(
        self,
        user_id: uuid.UUID,
        order_id: uuid.UUID,
        payload: schemas.UpdateOrderItemStatus,
    ) -> Order:
        """
        Update status of order items.

        Args:
            user_id: ID of the user
            payload: Status update information

        Returns:
            Updated Order instance

        Raises:
            HTTPException: If order cannot be updated
        """
        order = await self._service.filter_obj(
            get_first=True,
            check=dict(id=order_id, user_id=user_id),
            raise_error=True,
        )

        if order.status in [
            schemas.OrderStatus.CANCELLED,
            schemas.OrderStatus.COMPLETED,
        ]:
            raise get_error_response(
                detail=f"A {order.status.lower()} order cannot be updated",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        for item in order.order_items:
            if item.id in payload.product_id:
                if payload.status == schemas.OrderProductStatus.RETURNED:
                    product = await self.__product_service.__service.get(
                        id=item.id, raise_error=True
                    )
                    product.quantity += item.quantity
                    await product.save()
                item.status = payload.status

        return await order.save()

    async def update_order_status(
        self,
        payload: schemas.UpdateOrder,
        order_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Order:
        """
        Update order status.

        Args:
            payload: Status update information
            user_id: Optional user ID for filtering

        Returns:
            Updated Order instance
        """
        check = {"id": order_id}
        if user_id:
            check["user_id"] = user_id

        order = await self._service.filter_obj(
            get_first=True,
            check=check,
            raise_error=True,
        )

        if order.status == schemas.OrderStatus.CANCELLED:
            raise get_error_response(
                detail="A canceled order cannot be updated",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if payload.status == schemas.OrderStatus.CANCELLED:
            for item in order.order_items:
                if item.id:
                    product = await self.__product_service.__service.get(id=item.id)
                    product.quantity += item.quantity
                    await product.save()

        return await self._service.update(
            id=order_id,
            check=check,
            payload=dict(status=payload.status),
        )

    async def get_orders(
        self,
        params: QueryTypeWithoutLoadRelated,
        user_id: Optional[uuid.UUID] = None,
    ):
        """
        Retrieve all orders with optional filtering.

        Args:
            params: Query parameters for filtering and pagination
            user_id: Optional user ID for filtering

        Returns:
            List of Order instances
        """
        check = {}
        filter_conditions = []

        if params.filter_string:
            filter_conditions.append(
                or_.from_kwargs(
                    orderId__icontains=params.filter_string,
                    status__icontains=params.filter_string,
                    user__first_name__icontains=params.filter_string,
                    user__last_name__icontains=params.filter_string,
                    user__email__icontains=params.filter_string,
                )
            )

        if user_id:
            check["user_id"] = user_id

        return await self._service.filter_and_list(
            check=check,
            check_list=filter_conditions if filter_conditions else None,
            **params.model_dump(exclude={"filter_string"}),
        )

    async def get_order(
        self,
        order_id: uuid.UUID,
        params: GetSingleParams,
        user_id: Optional[uuid.UUID] = None,
    ):
        """
        Retrieve a single order.

        Args:
            order_id: ID of the order to retrieve
            params: Query parameters
            user_id: Optional user ID for filtering

        Returns:
            Order instance
        """
        check = {"id": order_id}
        if user_id:
            check["user_id"] = user_id

        return await self._service.get_single(
            check=check,
            **params.model_dump(),
        )
