from datetime import datetime
from decimal import Decimal
import hmac
import hashlib
import json
import typing as t
import uuid
from esmerald import Request, status
from edgy import or_
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.apps.orders.service import OrderService
from nprOlusolaBe.apps.orders.v1.schemas import OrderStatus
from nprOlusolaBe.apps.payment.models import Payment, get_payment_reference
from nprOlusolaBe.apps.payment.paystack.charge.schemas import (
    IChargeRequest,
    IChargeResponse,
)
from nprOlusolaBe.apps.payment.paystack.charge.services import (
    TransactionCharge,
)
from nprOlusolaBe.apps.payment.paystack.enum import PaymentCurrency, PaymentStatus
from nprOlusolaBe.apps.payment.v1.schemas import (
    FilterDateRange,
    ICreatePaymentIn,
    IPaymentVerificationIn,
)
from nprOlusolaBe.configs import settings as config

from nprOlusolaBe.core.schema import IFilterList, IFilterSingle, IResponseMessage
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.utils.base_response import (
    get_error_response,
    get_response,
)

from nprOlusolaBe.utils.ip_checker import get_ip_address
from nprOlusolaBe.utils.list_endpoint_query_params import GetSingleParams, QueryType


class PaymentService:
    _service = BaseService[Payment](model=Payment, model_name="payment")
    _order_service = OrderService()
    _transaction_charge = TransactionCharge()

    async def create(
        self,
        payload: ICreatePaymentIn,
        user: User,
        request: Request,
    ) -> IResponseMessage:
        check_order = await self._order_service._service.get(id=payload.order_id)
        if not check_order.user_id == user.id:
            raise get_error_response(
                detail=f"Order '{payload.order_id}' not  found",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if check_order.status == OrderStatus.CANCELLED:
            raise get_error_response(
                detail=f"Order '{payload.order_id}' is cancelled",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if check_order.status == OrderStatus.COMPLETED:
            raise get_error_response(
                detail=f"Order '{payload.order_id}' is completed",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        total_price = Decimal(0.00)
        for item in check_order.order_items:
            total_price += item.price * item.quantity

        char_schema = IChargeRequest(
            email=user.email,
            amount=int(total_price) * 100,
            currency=PaymentCurrency.NGN,
            reference=get_payment_reference(),
            callback_url=f"{config.project_url}/payments/verify",  # TOdo: change this to real frontend url settings
            metadata=dict(
                user_id=user.id,
                order_id=check_order.id,
                ip_address=get_ip_address(request),
            ),
        )
        charge_request = await self._transaction_charge.create_charge(
            payload=char_schema
        )
        new_payment = await self._service.create(
            payload=dict(
                order=check_order,
                total=total_price,
                reference=char_schema.reference,
                currency=PaymentCurrency.NGN,
                user=user,
                extra_data=charge_request.data.model_dump(),
                payment_url=charge_request.data.authorization_url,
            )
        )
        return get_response(
            data={"payment_url": new_payment.payment_url},
            status_code=status.HTTP_201_CREATED,
        )

    async def verify_charges_via_webhook(
        self,
        payload: IChargeResponse,
        request: Request,
    ) -> IResponseMessage:
        hash = hmac.new(
            config.paystack_secret_key.encode(),
            json.dumps(payload.model_dump()).encode(),
            hashlib.sha512,
        ).hexdigest()
        if hash == request.headers.get("x-paystack-signature"):
            get_payment = await self._service.filter_obj(
                check=dict(reference=payload.data.reference),
                get_first=True,
                raise_error=True,
            )

            is_completed = False

            if payload.data.status == "success":
                is_completed = True

            get_order: Order = await get_payment.order.load()
            if payload.data.status == PaymentStatus.FAILED:
                await self._order_service.update_order_status(
                    payload={"status": OrderStatus.CANCELLED}
                )
                raise get_error_response(
                    detail=f"Payment '{payload.reference}' failed",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if payload.data.status == PaymentStatus.SUCCESS:
                get_order.status = OrderStatus.READY_FOR_SHIPMENT
                await get_order.save()
                if await self._service.update(
                    id=get_payment.id,
                    payload=dict(
                        status=payload.data.status,
                        is_completed=is_completed,
                        verified_at=datetime.now().date(),
                        is_verified=is_completed,
                        extra_data=dict(
                            **get_payment.extra_data,
                            **payload.model_dump(),
                        ),
                    ),
                ):
                    # Todo: send a backegound task to send a sse to frontend

                    return get_response(
                        data=f"{self._service.model_name} status was changes",
                        status_code=status.HTTP_200_OK,
                    )
            raise get_error_response(
                detail=f"Error validating {self._service.model_name}"
            )

    async def verify_charges_via_callback(
        self, payload: IPaymentVerificationIn
    ) -> IResponseMessage:
        response = await self._transaction_charge.charge_verification(
            payment_reference=payload.reference
        )
        get_payment = await self._service.filter_obj(
            check=dict(reference=payload.reference),
            get_first=True,
            raise_error=True,
        )

        if response.data.status == "success":
            is_completed = True

        get_order: Order = await get_payment.order.load()
        if response.data.status == PaymentStatus.FAILED:
            await self._order_service.update_order_status(
                payload={"status": OrderStatus.CANCELLED}
            )
            raise get_error_response(
                detail=f"Payment '{payload.reference}' failed",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if response.data.status == PaymentStatus.SUCCESS:
            get_order.status = OrderStatus.READY_FOR_SHIPMENT
            await get_order.save()

            if await self._service.update(
                id=get_payment.id,
                payload=dict(
                    status=response.data.status,
                    is_completed=is_completed,
                    verified_at=datetime.now().date(),
                    extra_data=dict(
                        **get_payment.extra_data,
                        **response.model_dump(),
                    ),
                ),
            ):

                if response.status is PaymentStatus.PROCESSING:
                    return get_response(
                        data="Awaiting payment status change, please try again shortly",
                        status_code=status.HTTP_200_OK,
                    )
                return get_response(
                    data="payment status was updated successfully",
                    status_code=status.HTTP_200_OK,
                )
            raise get_error_response(
                detail=f"Error validating {self._service.model_name}"
            )

    async def get(
        self,
        params: GetSingleParams,
        payment_id: uuid.UUID,
        user_id: uuid.UUID = None,
    ) -> IFilterSingle:
        checks = {}
        if user_id:
            checks["user_id"] = user_id
        return await self._service.get_single(
            check=checks,
            object_id=payment_id,
            raise_error=True,
            **params.model_dump(),
        )

    async def filter_and_list(
        self,
        params: QueryType,
        user_id: str = None,
        is_completed: bool = None,
        is_trash: bool = None,
    ) -> IFilterList:
        check_list = []
        checks = {}
        if user_id:
            checks["user_id"] = user_id
        if is_completed:
            checks["is_completed"] = is_completed
        if is_trash:
            checks["is_trash"] = is_trash
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    user__email__icontains=params.filter_string,
                    user__first_name__icontains=params.filter_string,
                    user__last_name__icontains=params.filter_string,
                    reference__icontains=params.filter_string,
                    status__icontains=params.filter_string,
                    currency__icontains=params.filter_string,
                )
            )

        return await self._service.filter_and_list(
            check_list=check_list,
            check=checks,
            **params.model_dump(exclude={"filter_string"}),
        )

    async def get_revenue_trend(self) -> IResponseMessage:
        current_date = datetime.now()
        daily_sales = await self._service.query.filter(
            verified_at__day=current_date.day,
            is_completed=True,
        ).sum("amount")

        weekly_sales = await self._service.query.filter(
            verified_at__week=current_date.isocalendar()[1],
            is_completed=True,
        ).sum("amount")
        monthly_sales = await self._service.query.filter(
            verified_at__month=current_date.month,
            is_completed=True,
        ).sum("amount")
        yearly_sales = await self._service.query.filter(
            created_at__year=current_date.year
        ).sum("amount")
        return get_response(
            data=dict(
                daily=daily_sales,
                weekly=weekly_sales,
                monthly=monthly_sales,
                yearly=yearly_sales,
            )
        )

    async def get_revenue_sum_in_date_range(
        self,
        payload: FilterDateRange,
    ) -> t.Optional[IResponseMessage]:
        result = await self._service.query.filter(
            verified_at__gte=payload.start_date,
            verified_at__lte=payload.end_date,
        ).sum("amount")
        return get_response(data=dict(result=result))
