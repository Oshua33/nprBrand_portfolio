from decimal import Decimal
from uuid import uuid4
from nprOlusolaBe.apps.orders.models import Order
from nprOlusolaBe.apps.orders.v1.schemas import OrderStatus, OrderProductIn
from nprOlusolaBe.apps.account.models import User



def test_create_order_model():
    
    test_user = User(
        username="test_user",
        first_name="Test",
        last_name="User",
        email="test_user@example.com",
        password="securepassword123"
    )
    
    
    test_order_item = OrderProductIn(
        id=uuid4(),  # UUID for the product ID
        name="Test Product",
        price=Decimal("10.99"),
        image_url="http://example.com/image.jpg",
        quantity=2
    )
    
    testing_data = dict(
        user=test_user,
        order_items=[test_order_item],
        orderId="testID",
        status=OrderStatus.PENDING 
    )
    new_order = Order(
        user=testing_data.get("user"),
        order_items=testing_data.get("order_items"),
        orderId=testing_data.get("orderId"),
        status=testing_data.get("status"),
    )

    assert new_order.user == testing_data.get("user")
    assert new_order.order_items == testing_data.get("order_items")
    assert new_order.orderId == testing_data.get("orderId")
    assert new_order.status == testing_data.get("status")
