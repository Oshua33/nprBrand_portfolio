from uuid import UUID
from esmerald import Stream
from esmerald import (
    APIView,
    Query,
    Request,
    delete,
    get,
    Inject,
    Injects,
    post,
    put,
    status,
)
from nprOlusolaBe.apps.blog.service import (
    BlogCommentService,
    BlogLikeService,
    BlogService,
    BlogCategoryService,
    BlogTagService,
)
from nprOlusolaBe.apps.blog.models import (
    Blog,
    BlogCategory,
    BlogComment,
    BlogLike,
    BlogTag,
)
from esmerald import APIView, Query, delete, get, Inject, Injects, post, put, status
from nprOlusolaBe.apps.blog.service import BlogCategoryService, BlogService
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    ICount,
    IFilterList,
    IFilterSingle,
    QueryTypeWithoutLoadRelated,
)
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    QueryType,
    query_params_without_load_related,
    single_details_params,
    response,
)
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request
from nprOlusolaBe.apps.blog.v1 import schemas
from nprOlusolaBe.middleware.permission import IsCustomer, IsAdminOrSuperAdmin
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware


class BlogAPIView(APIView):
    path = "/blogs"
    tags = ["Blog management"]
    dependencies = {"service": Inject(BlogService)}

    @get("/", dependencies={"params": Inject(query_params)})
    async def get_all(
        self,
        params: QueryType = Injects(),
        service: BlogService = Injects(),
        is_publish: bool | None = None,
    ) -> IFilterList | list[Blog] | Stream:
        return await service.get_all(params=params, is_publish=is_publish)


    @get(
        "/{blog_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_blog_details(
        self,
        blog_id: UUID,
        is_publish: bool | None = Query(default=None),
        params: GetSingleParams = Injects(),
        service: BlogService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            blog_id=blog_id,
            params=params,
            is_publish=is_publish,
        )

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        # middleware=[JWTAuthMiddleware],
        # permissions=[IsAdminOrSuperAdmin]
    )
    async def create_blog(
        self,
        payload: schemas.BlogIn,
        service: BlogService = Injects(),
    ) -> Blog:
        return await service.create(payload=payload)

    @put(
        "/{blog_id}",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        # permissions=[IsAdminOrSuperAdmin],
        # middleware=[JWTAuthMiddleware]
    )
    async def update_blog(
        self,
        blog_id: UUID,
        payload: schemas.BlogIn,
        service: BlogService = Injects(),
    ) -> Blog:
        return await service.update(blog_id=blog_id, payload=payload)

    @delete(
        "/{blog_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsAdminOrSuperAdmin]
    )
    async def delete_blog(
        self, blog_id: UUID, service: BlogService = Injects()
    ) -> Blog:
        return await service.delete(blog_id=blog_id)


class BlogCategoryAPIView(APIView):
    path = "/blog_categories"
    tags = ["Blog Category management"]
    dependencies = {"service": Inject(BlogCategoryService)}
    middleware = [JWTAuthMiddleware]
    permissions = [IsAdminOrSuperAdmin]

    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create_category(
        self,
        payload: schemas.BlogCategoryIn,
        service: BlogCategoryService = Injects(),
    ) -> BlogCategory:
        return await service.create_category(payload=payload)

    @get("/", dependencies={"params": Inject(query_params_without_load_related)})
    async def get_all(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: BlogCategoryService = Injects(),
    ) -> IFilterList | list[BlogCategory] | Stream:
        return await service.get_all(
            params=params,
        )

    @get("/{category_id}", responses=response)
    async def get_blog_categories(
        self,
        category_id: UUID,
        service: BlogCategoryService = Injects(),
    ) -> BlogCategory:
        return await service.get(category_id=category_id)

    @put("/{category_id}", status_code=status.HTTP_201_CREATED, responses=response)
    async def update_category(
        self,
        category_id: UUID,
        payload: schemas.BlogCategoryIn,
        service: BlogCategoryService = Injects(),
    ) -> BlogCategory:
        return await service.update(category_id=category_id, payload=payload)

    @delete("/{category_id}", status_code=status.HTTP_200_OK, responses=response)
    async def delete_category(
        self, category_id: UUID, service: BlogCategoryService = Injects()
    ) -> BlogCategory:
        return await service.delete(category_id=category_id)


class BlogTagAPIView(APIView):
    path = "/blog_tags"
    tags = ["Blog tag management"]
    dependencies = {"service": Inject(BlogTagService)}
    middleware = [JWTAuthMiddleware]
    permissions = [IsAdminOrSuperAdmin]

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
    )
    async def create_tag(
        self,
        payload: schemas.BlogTagIn,
        service: BlogTagService = Injects(),
    ) -> BlogTag:
        return await service.create_tag(payload=payload)

    @get("/", dependencies={"params": Inject(query_params_without_load_related)})
    async def get_all(
        self,
        params: QueryTypeWithoutLoadRelated = Injects(),
        service: BlogTagService = Injects(),
    ) -> IFilterList | list[BlogTag] | Stream:
        return await service.get_all(
            params=params,
        )

    @get("/{tag_id}", responses=response)
    async def get_tag(
        self,
        tag_id: UUID,
        service: BlogTagService = Injects(),
    ) -> BlogTag:
        return await service.get(tag_id=tag_id)

    @put("/{tag_id}", status_code=status.HTTP_201_CREATED, responses=response)
    async def update_tag(
        self,
        tag_id: UUID,
        payload: schemas.BlogTagIn,
        service: BlogTagService = Injects(),
    ) -> BlogTag:
        return await service.update(tag_id=tag_id, payload=payload)

    @delete("/{tag_id}", status_code=status.HTTP_200_OK, responses=response)
    async def delete_tag(
        self, tag_id: UUID, service: BlogTagService = Injects()
    ) -> BlogTag:
        return await service.delete(tag_id=tag_id)


class BlogLikeAPIView(APIView):
    path = "/blog_likes"
    tags = ["Blog Like Management"]
    dependencies = {"service": Inject(BlogLikeService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
    )
    async def create_like(
        self,
        payload: schemas.BlogLikeIn,
        request: Request,
        service: BlogLikeService = Injects(),
    ) -> BlogLike:
        return await service.create_like(
            user_id=get_owner_view_id_from_request(request),
            payload=payload,
        )

    @delete(
        "/",
        status_code=status.HTTP_200_OK,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
        responses=response,
    )
    async def delete_like(
        self,
        request: Request,
        payload: schemas.BlogLikeIn,
        service: BlogLikeService = Injects(),
    ) -> BlogLike:
        return await service.delete_like(
            user_id=get_owner_view_id_from_request(request), payload=payload
        )

    @get("/{blog_id}/likes/count", responses=response)
    async def count_likes(
        self, blog_id: UUID, service: BlogLikeService = Injects()
    ) -> ICount:
        return await service.count_likes(blog_id=blog_id)


class BlogCommentAPIView(APIView):
    path = "/blog_comments"
    tags = ["Blog Comment Management"]
    dependencies = {"service": Inject(BlogCommentService)}

    @post(
        "/",
        status_code=status.HTTP_201_CREATED,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
        responses=response,
    )
    async def create_comment(
        self,
        request: Request,
        payload: schemas.BlogCommentIn,
        service: BlogCommentService = Injects(),
    ) -> BlogComment:
        return await service.create_comment(
            user_id=get_owner_view_id_from_request(request),
            payload=payload,
        )

    @get("/", dependencies={"params": Inject(query_params)})
    async def get_all_comments(
        self,
        params: QueryType = Injects(),
        service: BlogCommentService = Injects(),
    ) -> IFilterList | list[BlogComment] | Stream:
        return await service.get_all(params=params)

    @get(
        "/{comment_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
    )
    async def get_comment(
        self,
        comment_id: UUID,
        params: GetSingleParams = Injects(),
        service: BlogCommentService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            comment_id=comment_id,
            params=params,
        )

    @put(
        "/{comment_id}",
        status_code=status.HTTP_201_CREATED,
        responses=response,
        permissions=[IsCustomer],
        middleware=[JWTAuthMiddleware],
    )
    async def update_comment(
        self,
        comment_id: UUID,
        request: Request,
        payload: schemas.BlogCommentIn,
        service: BlogCommentService = Injects(),
    ) -> BlogComment:
        return await service.update(
            comment_id=comment_id,
            payload=payload,
            user_id=get_owner_view_id_from_request(request),
        )

    @delete(
        "/{comment_id}",
        status_code=status.HTTP_200_OK,
        responses=response,
        permissions=[IsCustomer],
        middleware=[JWTAuthMiddleware],
    )
    async def delete_comment(
        self,
        comment_id: UUID,
        request: Request,
        service: BlogCommentService = Injects(),
    ) -> BlogComment:
        return await service.delete(
            comment_id=comment_id,
            user_id=get_owner_view_id_from_request(request),
        )
