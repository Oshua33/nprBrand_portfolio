import asyncio
import uuid
from esmerald import status
from edgy import and_, or_
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    QueryType,
    QueryTypeWithoutLoadRelated,
)
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.blog.models import (
    Blog,
    BlogCategory,
    BlogComment,
    BlogTag,
    BlogLike,
)
from nprOlusolaBe.apps.blog.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response
from nprOlusolaBe.apps.label.service import LabelService
from nprOlusolaBe.apps.media.service import MediaService


class BlogCategoryService:
    _service = BaseService[BlogCategory](model=BlogCategory, model_name="Blog Category")

    async def create_category(self, payload: schemas.BlogCategoryIn):
        return await self._service.get_or_create(
            payload=payload,
            check={"name": payload.name},
            raise_error=True,
        )

    async def get(self, category_id: uuid.UUID):
        return await self._service.get(id=category_id, raise_error=True)

    async def get_all(
        self,
        params: QueryTypeWithoutLoadRelated,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(name__icontains=params.filter_string),
            )
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )

    async def update(
        self, category_id: uuid.UUID, payload: schemas.BlogCategoryIn
    ) -> BlogCategory:
        check_category = await self._service.filter_obj(
            get_first=True, check={"name": payload.name}, raise_error=False
        )
        if check_category:
            raise get_error_response(
                f" A {self._service.model_name} with this name {payload.name} already exist",
                status_code=status.HTTP_409_CONFLICT,
            )
        return await self._service.update(id=category_id, payload=payload)

    async def delete(self, category_id: uuid.UUID):
        return await self._service.delete(id=category_id)


class BlogService:
    _service = BaseService[Blog](model=Blog, model_name="Blog")
    __media_service = MediaService()
    __label_service = LabelService()
    __blog_category_service = BlogCategoryService()

    async def create(self, payload: schemas.BlogIn):
        media_instance, label_instance, blog_category_instance = await asyncio.gather(
            self.__media_service.get_file(file_id=payload.image_id),
            self.__label_service.get(label_id=payload.label_id),
            self.__blog_category_service.get(category_id=payload.category_id),
        )

        # # Prepare payload with the fetched instances
        blog_data = payload.model_dump()
        blog_data["image"] = media_instance
        blog_data["label"] = label_instance
        blog_data["category"] = blog_category_instance

        return await self._service.get_or_create(
            payload=blog_data,
            check={"title": payload.title},
            raise_error=False,
        )

    async def update(self, blog_id: uuid.UUID, payload: schemas.BlogIn):
        await self._service.get(id=blog_id, raise_error=True)
        check_blog = await self._service.filter_obj(
            get_first=True,
            check={"title": payload.title},
            raise_error=False,
        )
        if check_blog and check_blog.id != blog_id:
            raise get_error_response(
                f" A {self._service.model_name} with this title {payload.title} already exist",
                status_code=status.HTTP_409_CONFLICT,
            )

        return await self._service.update(id=blog_id, payload=payload)

    async def get(
        self,
        blog_id: uuid.UUID,
        params: GetSingleParams,
        is_publish: bool | None = None,
    ):
        checks = {}
        if is_publish is not None:
            checks["is_publish"] = is_publish
        return await self._service.get_single(
            object_id=blog_id,
            check=checks,
            **params.model_dump(),
            raise_error=True,
        )

    async def delete(self, blog_id: uuid.UUID):
        return await self._service.delete(id=blog_id)

    async def get_all(self, params: QueryType, is_publish: bool | None = None):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    title__icontains=params.filter_string,
                    description__icontains=params.filter_string,
                    label__name__icontains=params.filter_string,
                    category__name__icontains=params.filter_string,
                    # tags__name__icontains=params.filter_string,
                )
            )

        if is_publish is not None:
            checks["is_publish"] = is_publish
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )
        return result


class BlogTagService:
    _service = BaseService[BlogTag](model=BlogTag, model_name="Blog tag")
    _blog_service = BlogService()

    async def create_tag(
        self,
        payload: schemas.BlogTagIn,
    ) -> BlogTag:
        return await self._service.get_or_create(
            payload=payload,
            check={"name": payload.name},
            raise_error=True,
        )

    async def get(self, tag_id: uuid.UUID):
        return await self._service.get_single(
            object_id=tag_id,
            raise_error=True,
        )

    async def get_all(self, params: QueryTypeWithoutLoadRelated):
        check_list = []
        if params.filter_string:
            check_list.append(or_.from_kwargs(name__icontains=params.filter_string))
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check_list=check_list,
            fetch_distinct=True,
        )

    async def update(self, tag_id: uuid.UUID, payload: schemas.BlogTagIn) -> BlogTag:
        check_tag = await self._service.filter_obj(
            get_first=True,
            check={"name": payload.name},
            raise_error=False,
        )
        if check_tag:
            raise get_error_response(
                f" A {self._service.model_name} with this name {payload.name} already exist",
                status_code=status.HTTP_409_CONFLICT,
            )

        return await self._service.update(id=tag_id, payload=payload)

    async def delete(self, tag_id: uuid.UUID):
        return await self._service.delete(id=tag_id)


class BlogLikeService:
    _service = BaseService[BlogLike](model=BlogLike, model_name="Blog Like")
    _blog_service = BlogService()

    async def create_like(
        self, payload: schemas.BlogLikeIn, user_id: uuid.UUID
    ) -> BlogLike:

        return await self._service.get_or_create(
            payload={"blog": payload.blog_id, "author": user_id},
            check={"blog__id": payload.blog_id, "author__id": user_id},
            raise_error=True,
        )

    async def delete_like(
        self,
        payload: schemas.BlogLikeIn,
        user_id: uuid.UUID,
    ):
        check_like = await self._service.filter_obj(
            check=dict(blog__id=payload.blog_id, author__id=user_id),
            get_first=True,
            raise_error=True,
        )
        return await self._service.delete(id=check_like.id)

    async def count_likes(self, blog_id: uuid.UUID):
        return await self._service.get_count(
            check={"blog__id": blog_id},
        )


class BlogCommentService:
    _service = BaseService[BlogComment](model=BlogComment, model_name="BlogComment")
    _blog_service = BlogService()

    async def create_comment(
        self,
        payload: schemas.BlogCommentIn,
        user_id: uuid.UUID,
    ):
        check_blog = await self._blog_service._service.get(
            id=payload.blog_id,
            raise_error=True,
        )

        return await self._service.get_or_create(
            payload={
                "blog": check_blog,
                "comment": payload.comment,
                "user": user_id,
            },
            check=dict(user__id=user_id),
        )

    async def get(self, comment_id: uuid.UUID, params: GetSingleParams):
        return await self._service.get_single(
            object_id=comment_id,
            **params.model_dump(),
            raise_error=True,
        )

    async def get_all(
        self,
        params: QueryType,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(or_.from_kwargs(comment__icontains=params.filter_string))
        return await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
        )

    async def update(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: schemas.BlogCommentIn,
    ) -> BlogComment:
        get_comment = await self._service.get(
            id=comment_id,
            raise_error=True,
        )
        if (
            get_comment.user.id == user_id
            and get_comment.comment.strip() == payload.comment.strip()
            and str(get_comment.blog.id) == payload.blog_id
        ):

            return get_comment

        return await self._service.update(
            id=comment_id,
            payload=dict(comment=payload.comment),
            check=dict(user__id=user_id, blog__id=payload.blog_id),
        )

    async def delete(self, comment_id: uuid.UUID, user_id: uuid.UUID):
        return await self._service.delete(
            id=comment_id,
            check=dict(user__id=user_id),
        )
