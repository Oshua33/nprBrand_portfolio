from uuid import uuid4
from datetime import datetime, timedelta
from nprOlusolaBe.apps.payment.v1 import schemas  

def test_create_payment_schema():
    # Testing ICreatePaymentIn
    payment_data = dict(order_id=uuid4())
    payment_schema = schemas.ICreatePaymentIn(**payment_data)
    assert payment_schema.order_id == payment_data["order_id"]

    # Testing FilterDateRange
    now = datetime.now()
    date_range_data = dict(start_date=now, end_date=now + timedelta(days=7))
    date_range_schema = schemas.FilterDateRange(**date_range_data)
    assert date_range_schema.start_date == date_range_data["start_date"]
    assert date_range_schema.end_date == date_range_data["end_date"]

    # Testing IPaymentVerificationIn
    verification_data = dict(reference="test-reference")
    verification_schema = schemas.IPaymentVerificationIn(**verification_data)
    assert verification_schema.reference == verification_data["reference"]

    # Testing CurrencyData
    currency_data = dict(currency="USD", amount=100)
    currency_schema = schemas.CurrencyData(**currency_data)
    assert currency_schema.currency == currency_data["currency"]
    assert currency_schema.amount == currency_data["amount"]

    # Verifying serialized output for ICreatePaymentIn
    serialized_payment_data = payment_schema.model_dump()
    for key, value in serialized_payment_data.items():
        assert value == payment_data[key]

    # Verifying serialized output for FilterDateRange
    serialized_date_range_data = date_range_schema.model_dump()
    for key, value in serialized_date_range_data.items():
        assert value == date_range_data[key]

    # Verifying serialized output for IPaymentVerificationIn
    serialized_verification_data = verification_schema.model_dump()
    for key, value in serialized_verification_data.items():
        assert value == verification_data[key]

    # Verifying serialized output for CurrencyData
    serialized_currency_data = currency_schema.model_dump()
    for key, value in serialized_currency_data.items():
        assert value == currency_data[key]
