from uuid import uuid4
from decimal import Decimal
from nprOlusolaBe.apps.orders.v1 import schemas

def test_create_orders_schema():
    testing_data = dict(
        id=uuid4(),
        name="test name",
        image_url="http://example.com",
        price=Decimal("10.00"),
        quantity=1,
        status=schemas.OrderProductStatus.PROCESSING
    )
    schema = schemas.OrderProductIn(**testing_data)
    assert schema.id == testing_data.get("id")
    assert schema.name == testing_data.get("name")
    assert schema.image_url == testing_data.get("image_url")
    assert schema.price == testing_data.get("price")
    assert schema.quantity == testing_data.get("quantity")
    assert schema.status == testing_data.get("status")
    
    
    
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


