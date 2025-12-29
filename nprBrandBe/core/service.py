import io
from dataclasses import dataclass
import math
import edgy
import orjson
from typing import Any, Dict, Generator, List, TypeVar, Generic
import uuid
from edgy import Model
from edgy import QuerySet
from esmerald import Stream, status
from pydantic import BaseModel
import openpyxl
from nprOlusolaBe.core.schema import (
    IFilterList,
    IFilterSingle,
    ICount,
    IFilterList,
    IFilterSingle,
    SortEnum,
)

from typing import List, Optional

from nprOlusolaBe.utils.base_response import get_error_response

ModelType = TypeVar("ModelType", bound=Model)


@dataclass(slots=True, kw_only=True)
class BaseService(Generic[ModelType]):
    model: ModelType | None = None
    model_name: str = "Object"
    __query: QuerySet = None

    def make_slug(self, name: str, random_length: int = 10) -> str:
        return f"{name.replace(' ', '-').replace('_', '-')[:30]}-{uuid.uuid4().hex[:random_length if random_length < 16 else 7].lower()}"

    @property
    def get_related(self):
        return [
            *self.get_related_m2m,
            *self.get_related_backward,
            *self.get_foreign_keys,
        ]

    @property
    def get_related_m2m(self):
        return set(
            key
            for key, value in self.model.meta.fields.items()
            if isinstance(value, edgy.ManyToMany)
            or isinstance(value, edgy.ManyToManyField)
        )

    @property
    def get_foreign_keys(self) -> set[str]:
        return set(
            key
            for key, value in self.model.meta.fields.items()
            if isinstance(value, edgy.ForeignKey)
        )

    @property
    def get_related_backward(self) -> set[str]:
        return set(
            # self.model.meta.model_references.keys(),
        )

    @property
    def fields(self) -> set[str]:
        return set(
            column
            for column in self.model.meta.fields.keys()
            if column
            not in set.union(
                self.get_related_backward,
                self.get_related,
            )
        )

    @property
    def query(self) -> QuerySet:
        if not self.__query:
            self.__query = self.model.query
        return self.__query

    @query.setter
    def query(self, value: edgy.Manager):
        self.__query = value

    async def get_single(
        self,
        object_id: str,
        check: dict = None,
        check_list: list = None,
        load_related: bool = False,
        raise_error: bool = True,
        object_only: bool = False,
        exclude_secrets: bool = True,
    ) -> IFilterSingle | ModelType:
        try:
            if not check:
                check = {}
            if not check_list:
                check_list = []
            query = self.query.filter(id=object_id)
            if exclude_secrets:
                query = query.exclude_secrets()
            if check_list:
                query = query.filter(*check_list)
            if check:
                query = query.filter(**check)
            if load_related:
                query = query.select_related(*self.get_related)

            query = query.order_by("-id")
            raw_result = await query.first()

            if not raw_result and raise_error:
                raise get_error_response(
                    detail=f"{self.model_name} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            elif not raw_result:
                return raw_result

            if object_only:
                return raw_result
            if load_related:
                results = await self.to_dict(raw_result=[raw_result])
                if len(results) > 0:
                    raw_result = results.pop(0)
            return IFilterSingle(data=raw_result, status=200)
        except edgy.ObjectNotFound as e:
            raise get_error_response(
                detail=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            raise e

    async def to_dict(self, raw_result: list[Model]) -> list[dict]:
        columns = (
            *self.get_related_backward,
            *self.get_related_backward,
            *self.get_related,
        )
        return [
            {
                **{
                    field_name: [
                        data.model_dump() for data in list(getattr(result, field_name))
                    ]
                    for field_name in self.get_related_backward
                    if hasattr(result, field_name)
                },
                **{
                    field_name: getattr(result, field_name).model_dump()
                    for field_name in self.get_related
                    if hasattr(result, field_name) and getattr(result, field_name)
                },
                **{
                    attr: getattr(result, attr)
                    for attr in self.fields
                    if not attr in columns and not attr.startswith("_")
                },
            }
            for result in raw_result
        ]

    async def filter_and_list(
        self,
        check: dict = None,
        check_list: tuple = None,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "id",
        sort_by: SortEnum = SortEnum.DESC,
        load_related: bool = False,
        total_count: int = None,
        select: str = None,
        object_only: bool = False,
        export_to_excel: bool = False,
        fetch_distinct: bool = False,
        exclude_secrets: bool = True,
    ) -> IFilterList | list[ModelType] | Stream:
        if not check:
            check = {}
        try:
            query = self.query
            if exclude_secrets:
                query = query.exclude_secrets()
            if check_list:
                query = query.filter(*check_list)
            if check:
                query = query.filter(**check)
            if fetch_distinct:
                query = query.distinct("id")
            if not check or check_list:
                query = query.all()

            if load_related and self.get_related:
                query = query.select_related(*self.get_related).exclude_secrets()
            if sort_by == SortEnum.ASC and order_by:
                query = query.order_by(
                    *[
                        f"{col.strip()}"
                        for col in order_by.split(",")
                        if col in self.fields
                    ]
                )
            elif sort_by == SortEnum.DESC:
                query = query.order_by(
                    *[
                        f"-{col.strip()}"
                        for col in order_by.split(",")
                        if col in self.fields
                    ]
                )
            else:
                query = query.order_by("-id")
            query = query.offset((page - 1) * per_page).limit(per_page)
            if select:
                query = query.values(
                    *[
                        col.strip()
                        for col in select.split(",")
                        if col.strip() in self.fields
                    ]
                )

            raw_result = await query

            if object_only:
                return raw_result
            if load_related and raw_result and not select and not export_to_excel:
                raw_result = await self.to_dict(raw_result=raw_result)
            if export_to_excel:
                return self.write_to_excel(models=raw_result, filename=self.model_name)
            if not total_count:
                get_count = await self.get_count(
                    check=check if check else None,
                    check_list=check_list if check_list else None,
                )
                total_pages = math.ceil(get_count.count / per_page)
                total_count = get_count.count if get_count else 0
            return IFilterList(
                data=raw_result,
                status=200,
                total_pages=total_pages,
            )
        except KeyError:
            raise get_error_response(
                detail="Error filtering data, invalid filtered key",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            raise e

    async def delete_by_ids(self, object_ids: List[int], check: dict = None) -> int:
        if not check:
            check = {}
        query = self.query
        if check:
            query.filter(**check)
        query = query.filter(id__in=object_ids)
        return await query.delete()

    async def delete_by_id(
        self, object_id: int, raise_error: bool = False
    ) -> ModelType:
        result = await self.query.filter(id=object_id).delete()
        if result <= 0:
            if raise_error:
                raise get_error_response(
                    f"{self.model_name} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            else:
                return result
        return result

    async def get_by_ids(self, object_ids: List[uuid.UUID]) -> list[ModelType]:
        return await self.query.filter(id__in=object_ids).all()

    async def get(self, id: str, raise_error: bool = False) -> Optional[ModelType]:
        query = self.query.filter(id=id)
        obj = await query.first()
        if obj is not None:
            return obj
        if raise_error and not obj:
            raise get_error_response(
                detail=f"{self.model_name} is not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return obj

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[ModelType]:
        return await self.query.all().offset(offset).limit(limit)

    async def filter_obj(
        self,
        get_first: bool = False,
        check: dict = None,
        check_list: tuple | set | list = (),
        load_related: bool = False,
        raise_error: bool = False,
        exclude_secrets: bool = True,
    ) -> List[ModelType] | ModelType:
        if not check:
            check = {}
        query = self.query
        if exclude_secrets:
            query.exclude_secrets()
        if load_related:
            query = query.prefetch_related(
                *self.get_related_backward,
                *self.get_related,
            )
        if get_first:
            result = await query.filter(*check_list, **check).first()
        else:
            result = await query.filter(*check_list, **check).all()
        if not result and raise_error:
            raise get_error_response(
                f"{self.model_name} does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return result

    async def get_count(
        self, check: dict = None, check_list: tuple | list | set = ()
    ) -> ICount:
        if not check:
            check = {}
        query = self.query
        if check_list:
            query = query.filter(*check_list)
        if check:
            query = query.filter(**check)
        result = await query.all().count()
        return ICount(count=result)

    async def create(
        self,
        payload: dict | BaseModel,
        to_dict: bool = False,
    ) -> ModelType:
        data_dict = (
            payload.model_dump(exclude_unset=True)
            if isinstance(payload, BaseModel)
            else payload
        )
        instance = await self.query.create(**data_dict)
        return dict(instance) if to_dict else instance

    def generate_excel_content(
        self, payload: List[ModelType | dict | BaseModel]
    ) -> Generator[bytes, None, None]:
        """
        Generate Excel content from a list of models or dictionaries.

        Args:
            payload: List of models or dictionaries to convert to Excel

        Yields:
            Excel file content as bytes

        Raises:
            HTTPException: If no data is available to generate Excel
        """

        def clean_dict(input_dict: Dict[str, Any]) -> Dict[str, Any]:
            """Remove unwanted keys from dictionary."""
            return {
                k: v
                for k, v in input_dict.items()
                if not (
                    str(k).startswith("_") or k in ("id", "pk") or k in self.get_related
                )
            }

        # Process and clean data
        data = []
        for model in payload:
            if not model:
                continue

            if isinstance(model, (BaseModel, Model)):
                model_dict = model.model_dump()
            elif isinstance(model, dict):
                model_dict = model.copy()
            else:
                continue
          
            cleaned_data = clean_dict(model_dict)
            if cleaned_data:
                data.append(cleaned_data)

        if not data:
            raise get_error_response(
                detail="No enough data found to generate excel",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Serialize data for consistency
        data = orjson.loads(orjson.dumps(data))

        # Generate Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.model_name

        # Write headers and data
        headers = tuple(data[0].keys())
        ws.append(headers)
        ws.extend([tuple(row.values()) for row in data])

        # Save to bytes buffer and yield
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        yield from buffer

    def write_to_excel(
        self, models: List[ModelType | dict | BaseModel], filename: str
    ) -> Stream:
        filename = f"{filename or self.model_name}.xlsx"

        return Stream(
            self.generate_excel_content(models),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    async def update(
        self, id: str, payload: BaseModel | dict, check: dict = None
    ) -> ModelType:
        query = self.query.filter(id=id)
        if check:
            checks = self.query.filter(**check).first()
            if checks:
                raise get_error_response(
                    f"{self.model_name} does not exist",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        instance: ModelType = await query.exclude_secrets().first()

        item = payload.model_dump() if isinstance(payload, BaseModel) else payload
        if not instance:
            raise get_error_response(
                f"{self.model_name} does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        for key, value in item.items():
            setattr(instance, key, value)
        await instance.save()
        return instance

    async def delete(self, id: uuid.UUID, check: dict = None) -> ModelType:
        try:
            if not check:
                check = {}
            instance = await self.filter_obj(
                check=dict(id=id, **check),
                get_first=True,
                raise_error=True,
            )
            await instance.delete()
            return instance

        except Exception as e:
            if str(e).find("IntegrityError"):
                raise get_error_response(
                    "Cannot delete record, because it is in use",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise get_error_response(
                str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def get_or_create(
        self,
        payload: BaseModel | dict,
        raise_error: bool = False,
        check: dict = None,
    ) -> ModelType:

        data_dict = payload.model_dump() if isinstance(payload, BaseModel) else payload
        check = check or {}
        check_item = await self.query.filter(**check).exclude_secrets().first()

        if check_item and raise_error:
            raise get_error_response(
                f"{self.model_name} already exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        elif not raise_error and check_item:
            return check_item
        check_item = await self.query.create(**data_dict)
        return check_item

    async def bulk_create(
        self,
        instances: List[dict],
        batch_size: int = 10,
    ) -> list[ModelType]:
        await self.query.bulk_create(instances)
        return instances

    async def bulk_update(self, instances: List[ModelType]) -> list[ModelType]:
        fields = self.fields
        current_columns = set()
        if self.get_related:
            current_columns.update(self.get_related)
        if self.get_related_backward:
            current_columns.update(self.get_related_backward)
        if current_columns:
            for column in current_columns:
                if column in fields:
                    fields.remove(column)

        return await self.query.bulk_update(
            instances,
            fields=fields,
            #     batch_size=10,
        )

    async def bulk_delete(self, objs: List[ModelType]) -> list[ModelType]:
        ids = [obj.id for obj in objs]
        result = await self.query.filter(id__in=ids).delete()
        return objs if result else None
