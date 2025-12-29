import uuid
from esmerald import status
from edgy import or_
from nprOlusolaBe.core.schema import (
    QueryType,
    GetSingleParams,
)
from nprOlusolaBe.apps.product.models import (
    Product,
    ProductCategory,
)
from nprOlusolaBe.apps.product.v1 import schemas
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.media.service import MediaService
from nprOlusolaBe.utils.base_response import get_error_response


class ProductService:
    _service = BaseService[Product](model=Product, model_name="Product")
    _media_service = MediaService()

    async def create(self, payload: schemas.ProductIn):

        from nprOlusolaBe.apps.product.service import ProductCategoryService

        _product_category_service = ProductCategoryService()

        media_instance = await self._media_service.get_file(file_id=payload.image_id)
        category_instance = await _product_category_service.get(
            category_id=payload.category_id
        )

        if (
            payload.quantity == 0
            and payload.status is not schemas.ProductStatus.OUT_OF_STOCK
        ):
            raise get_error_response(
                "Cannot set a product to `in stock` when quantity is 0",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        Product_data = payload.model_dump()
        Product_data["image"] = media_instance
        Product_data["category"] = category_instance

        return await self._service.get_or_create(
            payload=Product_data,
            check={"name": payload.name},
            raise_error=True,
        )

    async def get(
        self,
        product_id: uuid.UUID,
        params: GetSingleParams,
        status: schemas.ProductStatus | None = None,
        is_trash: bool = None,
    ):
        check = {}
        if status is not None:
            check["status"] = status
        if is_trash is not None:
            check["is_trash"] = is_trash
        return await self._service.get_single(
            object_id=product_id,
            check=check,
            raise_error=True,
            **params.model_dump(),
        )

    async def get_all(
        self,
        params: QueryType,
        status: schemas.ProductStatus = None,
        is_trash: bool = None,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    name__icontains=params.filter_string,
                    content__icontains=params.filter_string,
                    category__name__icontains=params.filter_string,
                )
            )
        if status is not None:
            checks["status"] = status
        if is_trash is not None:
            checks["is_trash"] = is_trash

        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )

    async def delete(self, product_id: uuid.UUID, is_trash: bool = True):
        item = await self._service.get(id=product_id, raise_error=True)
        if not is_trash and item:
            return await self._service.delete(id=product_id)
        return self._service.update(id=product_id, payload=dict(is_trash=is_trash))

    async def update(
        self,
        product_id: uuid.UUID,
        payload: schemas.ProductIn,
    ):
        check = await self._service.filter_obj(
            get_first=True,
            check={"name": payload.name, "id__not": product_id},
            raise_error=False,
        )
        if (
            payload.quantity == 0
            and payload.status is not schemas.ProductStatus.OUT_OF_STOCK
        ):
            raise get_error_response(
                "Cannot set a product to `in stock` when quantity is 0",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if check:
            raise get_error_response(
                f"A {self._service.model_name} with this name {payload.name} already exist"
            )

        return await self._service.update(
            id=product_id,
            payload=payload,
        )

    async def set_availability(
        self,
        product_id: uuid.UUID,
        payload: schemas.ProductAvailable,
    ):
        product: Product = await self._service.get_single(
            object_id=product_id, object_only=True
        )
        stock = payload.quantity
        if stock == 0:
            product.status = schemas.ProductStatus.OUT_OF_STOCK
        elif stock <= 3:
            product.status = schemas.ProductStatus.LIMITED_STOCK
        else:
            product.status = schemas.ProductStatus.IN_STOCK
        return await product.save()


class ProductCategoryService:
    _service = BaseService[ProductCategory](
        model=ProductCategory, model_name="Product category"
    )

    async def create_category(self, payload: schemas.ProductCategoryIn):
        return await self._service.get_or_create(
            payload=payload, check={"name": payload.name}, raise_error=True
        )

    async def get(self, category_id: uuid.UUID):
        return await self._service.get(id=category_id, raise_error=True)

    async def get_all(
        self,
        params: QueryType,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(or_.from_kwargs(name__icontains=params.filter_string))
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )

    async def update(
        self, category_id: uuid.UUID, payload: schemas.ProductCategoryIn
    ) -> ProductCategory:
        check = await self._service.filter_obj(
            get_first=True,
            check={"name": payload.name, "id__not": category_id},
            raise_error=False,
        )
        if check:
            raise get_error_response(
                detail=f"A {self._service.model_name} with this name {payload.name} already exist",
                status_code=status.HTTP_409_CONFLICT,
            )
        return await self._service.update(
            id=category_id,
            payload=payload,
        )

    async def delete(self, category_id: uuid.UUID) -> ProductCategory:
        return await self._service.delete(id=category_id)
