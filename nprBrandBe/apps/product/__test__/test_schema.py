from uuid import uuid4
from decimal import Decimal
from nprOlusolaBe.apps.product.v1.schemas import ProductIn, ProductStatus, ProductMetaData, ExternalProductLink

def test_create_product_schema():
    # Example valid meta_data and external_links
    meta_data = [ProductMetaData(key="example_key", value="example_value")]
    external_links = [ExternalProductLink(name="example link", link="http://example.com")]

    testing_data = dict(
        name="test name",
        content="test content",
        price=Decimal("10.00"),
        image_id=uuid4(),
        quantity=1,
        status=ProductStatus.LIMITED_STOCK,
        meta_data=meta_data,
        external_links=external_links,
        category_id=uuid4()
    )
    
    # Create ProductIn schema instance
    schema = ProductIn(**testing_data)

    # Compare simple fields
    assert schema.name == testing_data["name"]
    assert schema.content == testing_data["content"]
    assert schema.price == testing_data["price"]
    assert schema.image_id == testing_data["image_id"]
    assert schema.quantity == testing_data["quantity"]
    assert schema.status == testing_data["status"]
    assert schema.category_id == testing_data["category_id"]

    # Correct comparison for meta_data and external_links using model_dump()
    assert [meta.model_dump() for meta in schema.meta_data] == [m.model_dump() for m in meta_data]
    assert [link.model_dump() for link in schema.external_links] == [l.model_dump() for l in external_links]

    # Compare dumped schema with testing_data after normalizing complex types
    passed_data = schema.model_dump()
    
    for key, value in passed_data.items():
        if key in ["meta_data", "external_links"]:
            # Normalize both sides for proper comparison
            assert value == [item.model_dump() for item in testing_data[key]]
        else:
            assert value == testing_data[key]


# from uuid import uuid4
# from decimal import Decimal
# from nprOlusolaBe.apps.product.v1.schemas import ProductIn, ProductStatus, ProductMetaData, ExternalProductLink


# def test_create_product_schema():
#     # Example valid meta_data and external_links
#     meta_data = [ProductMetaData(key="example_key", value="example_value")]
#     external_links = [ExternalProductLink(name="example link", link="http://example.com")]

#     testing_data = dict(
#         name="test name",
#         content="test content",
#         price=Decimal("10.00"),
#         image_id=uuid4(),
#         quantity=1,
#         status=ProductStatus.LIMITED_STOCK,
#         meta_data=meta_data,
#         external_links=external_links,
#         category_id=uuid4()
#     )
#     schema = ProductIn(**testing_data)

#     # Compare fields
#     assert schema.name == testing_data.get("name")
#     assert schema.content == testing_data.get("content")
#     assert schema.price == testing_data.get("price")
#     assert schema.image_id == testing_data.get("image_id")
#     assert schema.quantity == testing_data.get("quantity")
#     assert schema.status == testing_data.get("status")
#     assert [meta.dict() for meta in schema.meta_data] == [m.dict() for m in meta_data]
#     assert [link.dict() for link in schema.external_links] == [l.dict() for l in external_links]
#     assert schema.category_id == testing_data.get("category_id")

#     passed_data = schema.model_dump()
#     for key, value in passed_data.items():
#         assert value == testing_data.get(key)




# # def test_create_product_schema():
# #     # Example valid meta_data and external_links
# #     meta_data = [ProductMetaData(key="example_key", value="example_value")]
# #     external_links = [ExternalProductLink(name="example link", link="http://example.com")]

# #     testing_data = dict(
# #         name="test name",
# #         content="test content",
# #         price=Decimal("10.00"),
# #         image_id=uuid4(),
# #         quantity=1,
# #         status=ProductStatus.LIMITED_STOCK,
# #         meta_data=meta_data,
# #         external_links=external_links,
# #         category_id=uuid4()
# #     )
# #     schema = ProductIn(**testing_data)
# #     assert schema.name == testing_data.get("name")
# #     assert schema.content == testing_data.get("content")
# #     assert schema.price == testing_data.get("price")
# #     assert schema.image_id == testing_data.get("image_id")
# #     assert schema.quantity == testing_data.get("quantity")
# #     assert schema.status == testing_data.get("status")
# #     assert schema.meta_data == testing_data.get("meta_data")
# #     assert schema.external_links == testing_data.get("external_links")
# #     assert schema.category_id == testing_data.get("category_id")
    
# #     passed_data = schema.model_dump()
# #     for key, _ in passed_data.items():
# #         assert passed_data.get(key) == testing_data.get(key)


# # # FAILED nprOlusolaBe/apps/product/__test__/test_schema.py::test_create_product_schema - AssertionError: assert [{'key': 'exa...ample_value'}] == [ProductMetaD...ample_value')]