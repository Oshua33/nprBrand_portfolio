from typing import List
from uuid import UUID
from esmerald import Stream
from esmerald import APIView, Query, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.product.models import Product, ProductCategory
from nprOlusolaBe.apps.product.service import ProductCategoryService, ProductService
from nprOlusolaBe.core.schema import GetSingleParams, IFilterList, IFilterSingle
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params_without_load_related,
    QueryTypeWithoutLoadRelated,
    response,
    single_details_params,
)
from nprOlusolaBe.apps.product.v1 import schemas
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware


class ProductAPIView(APIView):
    path = "/products"
    tags = ["Product management"]
    dependencies = {"service": Inject(ProductService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware],
    )
    async def create_product(
        self,
        payload: schemas.ProductIn,
        service: ProductService = Injects(),
    ) -> Product:
        return await service.create(payload=payload)

    @get("/", dependencies={"params": Inject(query_params_without_load_related)})
    async def list_Product(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: ProductService = Injects(),
        status: schemas.ProductStatus | None = Query(default=None),
    ) -> IFilterList | List[Product] | Stream:
        return await service.get_all(
            params=params,
            status=status,
        )

    @get(
        "/{product_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_product_details(
        self,
        product_id: UUID,
        params: GetSingleParams = Injects(),
        status: schemas.ProductStatus | None = Query(default=None),
        service: ProductService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            product_id=product_id,
            status=status,
            params=params,
        )

    @put(
        "/{product_id}",
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware],
    )
    async def update_product_details(
        self,
        product_id: UUID,
        payload: schemas.ProductIn,
        service: ProductService = Injects(),
    ) -> Product:
        return await service.update(product_id=product_id, payload=payload)

    @put("/{product_id}/status", responses=response)
    async def set_product_status(
        self,
        product_id: UUID,
        payload: schemas.ProductAvailable,
        service: ProductService = Injects(),
    ) -> Product:
        return await service.set_availability(product_id=product_id, payload=payload)

    @delete(
        "/{product_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
        middleware=[JWTAuthMiddleware],
    )
    async def delete_product(
        self,
        product_id: UUID,
        service: ProductService = Injects(),
        is_trash: bool = Query(default=None),
    ) -> Product:
        return await service.delete(product_id=product_id, is_trash=is_trash)


class ProductCategoryAPIView(APIView):
    path = "/product_categories"
    tags = ["Product category management"]
    dependencies = {"service": Inject(ProductCategoryService)}
    middleware = [JWTAuthMiddleware]

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
    )
    async def create_category(
        self,
        payload: schemas.ProductCategoryIn,
        service: ProductCategoryService = Injects(),
    ) -> ProductCategory:
        return await service.create_category(payload=payload)

    @get("/", dependencies={"params": Inject(query_params_without_load_related)})
    async def list_categories(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: ProductCategoryService = Injects(),
    ) -> IFilterList | List[ProductCategory] | Stream:
        return await service.get_all(params=params)

    @get("/{category_id}", responses=response)
    async def get_category_details(
        self,
        category_id: UUID,
        service: ProductCategoryService = Injects(),
    ) -> ProductCategory:
        return await service.get(category_id=category_id)

    @put("/{category_id}", responses=response, permissions=[IsAdminOrSuperAdmin])
    async def update_product_category(
        self,
        category_id: UUID,
        payload: schemas.ProductCategoryIn,
        service: ProductCategoryService = Injects(),
    ) -> ProductCategory:
        return await service.update(category_id=category_id, payload=payload)

    @delete(
        "/{category_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        permissions=[IsAdminOrSuperAdmin],
    )
    async def delete_category(
        self,
        category_id: UUID,
        service: ProductCategoryService = Injects(),
    ) -> ProductCategory:
        return await service.delete(category_id=category_id)
