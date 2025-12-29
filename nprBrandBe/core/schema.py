from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict
from esmerald import status
from nprOlusolaBe.core import constant


class SortEnum(Enum):
    ASC = "asc"
    DESC = "desc"


class IHealthCheck(BaseModel):

    name: str
    version: float
    description: str
    docs_url: str
    redoc_url: str


class IResponseMessage(BaseModel):
    data: Any
    status_code: int = status.HTTP_200_OK


class IFilterList(BaseModel):
    previous: int | None = None
    next: int | None = None
    total_pages: int = 0
    data: List[Any] = []
    ConfigDict(from_attributes=True)


class IFilterSingle(BaseModel):
    data: Any
    status: int
    ConfigDict(from_attributes=True)


class ICount(BaseModel):
    count: int = 0


class IError(BaseModel):
    detail: str
    status_code: int = status.HTTP_401_UNAUTHORIZED


class GetSingleParams(BaseModel):
    load_related: bool = False


class QueryTypeWithoutLoadRelated(BaseModel):
    filter_string: Optional[str] = None
    page: int = constant.PAGINATION_PAGE
    per_page: int = constant.PAGINATION_PAGE_SIZE
    order_by: str = constant.DEFAULT_SORT_ORDER
    export_to_excel: bool = False
    sort_by: SortEnum = SortEnum.DESC
    select: Optional[str] = None


class QueryType(QueryTypeWithoutLoadRelated):
    load_related: bool = False
