from datetime import datetime
from esmerald import APIView, Inject, Injects, Request, get, post, put, status
from nprOlusolaBe.apps.payment.v1 import schemas
from nprOlusolaBe.apps.payment.paystack.charge.schemas import (
    IChargeResponse,
)
from nprOlusolaBe.core.schema import IFilterList, IFilterSingle, IResponseMessage
from nprOlusolaBe.utils.get_owner_by_id import (
    get_owner_view_id_from_request,
)
from nprOlusolaBe.utils.list_endpoint_query_params import (
    GetSingleParams,
    QueryType,
    query_params,
    query_params_without_load_related,
    response,
)

from nprOlusolaBe.apps.payment.service import PaymentService
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsAdminOrSuperAdmin, IsCustomer


class PaymentAPIView(APIView):
    path = "/payments"
    tags = ["Payments"]
    dependencies = {"service": Inject(PaymentService)}
    middleware = [JWTAuthMiddleware]
    permissions = [IsCustomer, IsAdminOrSuperAdmin]
    
    
    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create_payment(
        self,
        payload: schemas.ICreatePaymentIn,
        request: Request,
        service: PaymentService = Injects(),
    ) -> IResponseMessage:
        return await service.create(
            payload=payload,
            request=request,
            user=request.user,
        )

    @get(
        "/",
        dependencies={"params": Inject(query_params)},
    )
    async def get_payment_list(
        self,
        request: Request,
        params: QueryType = Injects(),
        is_completed: bool | None = None,
        is_trash: bool = False,
        service: PaymentService = Injects(),
    ) -> IFilterList:
        return await service.filter_and_list(
            params=params,
            user_id=get_owner_view_id_from_request(request, "id"),
            is_completed=is_completed,
            is_trash=is_trash,
        )

    @get(
        "/{payment_id}",
        dependencies={"params": Inject(query_params_without_load_related)},
    )
    async def get_payment(
        self,
        payment_id: str,
        request: Request,
        params: GetSingleParams = Injects(),
        service: PaymentService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            payment_id=payment_id,
            params=params,
            user_id=get_owner_view_id_from_request(request),
        )

    @put("/verify/callback")
    async def verify_payment(
        self,
        payload: schemas.IPaymentVerificationIn,
        service: PaymentService = Injects(),
    ) -> IResponseMessage:
        return await service.verify_charges_via_callback(
            payload=payload,
        )

    @put("/verify/webhook")
    async def verify_payment(
        self,
        payload: IChargeResponse,
        service: PaymentService = Injects(),
    ) -> IResponseMessage:
        return await service.verify_charges_via_webhook(
            payload=payload,
            request=Request,
        )

    @get("/revenue/analytics")
    async def get_revenue_analytics(
        self,
        service: PaymentService = Injects(),
    ) -> IResponseMessage:
        return await service.get_revenue_trend()

    @get("/revenue/{start_date}/{end_date}")
    async def get_revenue_analytics_from_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        service: PaymentService = Injects(),
    ) -> IResponseMessage:
        return await service.get_revenue_sum_in_date_range(
            payload=schemas.FilterDateRange(start_date=start_date, end_date=end_date),
        )
