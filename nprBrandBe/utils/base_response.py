from typing import Any
from esmerald import HTTPException, status
from pydantic import BaseModel
from nprOlusolaBe.core.schema import IResponseMessage


def get_response(
    data: Any,
    status_code: int = 200,
):
    data_map = {}
    if isinstance(data, BaseModel):
        data_map = data.model_dump()
    data_map = data

    return IResponseMessage(
        data=data_map,
        status_code=status_code,
    )


def get_error_response(
    detail: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> HTTPException:
    return HTTPException(
        detail=dict(
            message=detail,
            status_code=status_code,
        ),
        status_code=status_code,
    )
