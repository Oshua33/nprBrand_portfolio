from enum import Enum


class PaymentStatus(Enum):
    INITIALIZE = "initialize"
    COMPLETE = "complete"
    FAILED = "failed"
    PROCESSING = "processing"
    REFUNDED = "refunded"


class PaymentCurrency(Enum):
    NGN = "NGN"
    USD = "USD"
