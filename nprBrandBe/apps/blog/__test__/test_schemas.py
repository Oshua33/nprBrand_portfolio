from uuid import uuid4
from nprOlusolaBe.apps.blog.v1 import schemas

def test_create_blog_schema():
    testing_data = dict(
        title="test title",
        description="test content",
        image_id=uuid4(),
        is_publish= True,
        category_id=uuid4(),
        label_id=uuid4()
    )
    schema = schemas.BlogIn(**testing_data)
    assert schema.title == testing_data.get("title")
    assert schema.description == testing_data.get("description")
    assert schema.image_id == testing_data.get("image_id")
    assert schema.is_publish == testing_data.get("is_publish")
    assert schema.category_id == testing_data.get("category_id")
    assert schema.label_id == testing_data.get("label_id")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)



# from uuid import uuid4

# from nprOlusolaBe.apps.cart.v1 import schemas

# def test_create_cart_schema():
#     testing_data = dict(
#         user_id=uuid4(),
#         quantity=1,
#         product_id=uuid4()
#     )
#     schema = schemas.CartIn(**testing_data)
#     assert schema.user_id == testing_data.get("user_id")
#     assert schema.quantity == testing_data.get("quantity")
#     assert schema.product_id == testing_data.get("product_id")
#     passed_data = schema.model_dump()
#     for key, _ in passed_data.items():
#         assert testing_data.get(key) == testing_data.get(key)
