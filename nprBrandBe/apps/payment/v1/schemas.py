from datetime import datetime
import uuid
import pydantic as pyd


class ICreatePaymentIn(pyd.BaseModel):
    order_id: uuid.UUID


class FilterDateRange(pyd.BaseModel):
    start_date: datetime
    end_date: datetime


class IPaymentVerificationIn(pyd.BaseModel):
    reference: str


class CurrencyData(pyd.BaseModel):
    currency: str
    amount: int
