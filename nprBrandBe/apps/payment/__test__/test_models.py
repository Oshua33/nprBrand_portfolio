from decimal import Decimal
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.apps.orders.v1.schemas import OrderStatus
from nprOlusolaBe.apps.payment.models import Payment
from nprOlusolaBe.apps.payment.paystack.enum import PaymentStatus
from datetime import datetime

def test_create_payment_model():
    # Create a test user
    test_user = User(
        username="payment_tester",
        first_name="Payment",
        last_name="Tester",
        email="payment_tester@example.com",
        password="securepassword123"
    )
   

    # Create a test order
    test_order = Order(
        user=test_user,
        order_items=[],
        orderId="testOrder123",
        status=OrderStatus.PENDING 
    )
    

    # Create a Payment instance
    payment = Payment(
        total=Decimal("1500.00"),
        order=test_order,
        currency="NGN",
        user=test_user,
        is_trash=False,
        verified_at=None,
        promo_code={"code": "DISCOUNT10", "discount": 10},
        extra_data={"note": "First payment test"},
        payment_url="http://paymentgateway.com/checkout",
        status=PaymentStatus.INITIALIZE.value,
        is_completed=False,
        reference="TR-123456789",
    
    )


    # Assertions to verify the Payment instance
    assert payment.reference.startswith("TR-")  # Ensures the reference is auto-generated
    assert payment.total == Decimal("1500.00")
    assert payment.order == test_order
    assert payment.currency == "NGN"
    assert payment.user == test_user
    assert payment.promo_code == {"code": "DISCOUNT10", "discount": 10}
    assert payment.extra_data == {"note": "First payment test"}
    assert payment.payment_url == "http://paymentgateway.com/checkout"
    assert payment.status == PaymentStatus.INITIALIZE.value
    assert payment.is_completed is False
    assert payment.is_trash is False
    assert payment.verified_at is None
