from datetime import date
from typing import Optional
from esmerald import Query, Request
from esmerald.openapi.datastructures import OpenAPIResponse
from nprOlusolaBe.core import constant
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    IError,
    QueryType,
    QueryTypeWithoutLoadRelated,
    SortEnum,
)
from nprOlusolaBe.utils.base_response import get_error_response

response = {
    400: OpenAPIResponse(
        model=IError,
        description="All error response Body, except validation error occurred",
    )
}


def single_details_params(
    load_related: bool = Query(
        default=False,
        title="Load Related data from database",
        description="Load related data from database particular to each entity, defaults to `False`",
    ),
):
    return GetSingleParams(load_related=load_related)


def query_params(
    filter_string: Optional[str] = Query(
        default=None,
        description="Filter through the list of data",
        title="Filter string",
    ),
    page: int = Query(
        default=constant.PAGINATION_PAGE,
        title="paginator page number",
        description="paginator page number for listing the result",
        ge=constant.MIN_PAGINATION_LIMIT,
    ),
    per_page: int = Query(
        default=constant.PAGINATION_PAGE_SIZE,
        title="paginator data per page",
        description="paginator total result per page for listing the result",
        le=constant.MAX_PAGINATION_LIMIT,
        ge=constant.MIN_PAGINATION_LIMIT,
    ),
    order_by: str = Query(
        default=constant.DEFAULT_SORT_ORDER,
        title="Order by",
        description="Order the total result to be returned by database columns",
    ),
    export_to_excel: bool = Query(
        default=False,
        title="export to Excel",
        description=" whether to export the data result to Excel",
    ),
    sort_by: SortEnum = Query(
        default=SortEnum.DESC,
        title="Sort By",
        description=f"Sort the total result to be returned by either asc or desc, defaults to {SortEnum.DESC}",
    ),
    load_related: bool = Query(
        default=False,
        title="Load Related data from database",
        description="Load related data from database particular to each entity, defaults to `False`",
    ),
    select: Optional[str] = Query(
        default="",
        title="select specific data from database",
        description="Select specific data from this entity, e.g id, name, email. Default to None(meaning select all), it must be a string separated by comma, like `name, id, created_at, updated_at` if the data does not exist in the entitle table it will be returned",
    ),
) -> QueryType:
    return QueryType(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
        select=select,
        filter_string=filter_string,
        export_to_excel=export_to_excel,
    )


def query_params_without_load_related(
    filter_string: Optional[str] = Query(
        default=None,
        description="Filter through the list of data",
        title="Filter string",
    ),
    export_to_excel: bool = Query(
        default=False,
        title="export to Excel",
        description=" whether to export the data result to Excel",
    ),
    page: int = Query(
        default=constant.MIN_PAGINATION_LIMIT,
        title="paginator page number",
        description="paginator page number for listing the result",
        ge=constant.MIN_PAGINATION_LIMIT,
    ),
    per_page: int = Query(
        default=constant.MAX_PAGINATION_LIMIT,
        title="paginator data per page",
        description="paginator total result per page for listing the result",
        le=constant.MAX_PAGINATION_LIMIT,
        ge=constant.MIN_PAGINATION_LIMIT,
    ),
    order_by: str = Query(
        default=constant.DEFAULT_SORT_ORDER,
        title="Order by",
        description="Order the total result to be returned by database columns",
    ),
    sort_by: SortEnum = Query(
        default=SortEnum.DESC,
        title="Sort By",
        description=f"Sort the total result to be returned by either asc or desc, defaults to {SortEnum.DESC}",
    ),
    select: Optional[str] = Query(
        default="",
        title="select specific data from database",
        description="Select specific data from this entity, e.g id, name, email. Default to None(meaning select all), it must be a string separated by comma, like `name, id, created_at, updated_at` if the data does not exist in the entitle table it will be returned",
    ),
):
    return QueryTypeWithoutLoadRelated(
        page=page,
        per_page=per_page,
        order_by=order_by,
        sort_by=sort_by,
        select=select,
        filter_string=filter_string,
        export_to_excel=export_to_excel,
    )


class ValidateDateFromParams:
    def __init__(self, field_name: str = "date", is_optional=True):
        self.field_name = field_name
        self.is_optional = is_optional

    def parse_date(self, request: Request) -> Optional[date]:
        value = request.query_params.get(self.field_name, None)
        if value is None or value == "" and self.is_optional:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError as e:
            raise get_error_response(
                f"{self.field_name} is not a valid date", status_code=422
            ) from e
