# from uuid import uuid4
# from nprOlusolaBe.apps.event.v1 import schemas

# def test_create_event_schema():
#     testing_data = dict(
#         title="test title",
#         content="test content",
#         image_id=uuid4(),
#         start_time=date,
#         end_time=dateime,
#         start_date=datetime,
#         end_date=datetime
#         is_active= False,
#         url="https://www/mobile.com",
#         location="locate me "
#     )
#     schema = schemas.BlogIn(**testing_data)
#     assert schema.title == testing_data.get("title")
#     assert schema.description == testing_data.get("description")
#     assert schema.image_id == testing_data.get("image_id")
#     assert schema.is_publish == testing_data.get("is_publish")
#     assert schema.category_id == testing_data.get("category_id")
#     assert schema.label_id == testing_data.get("label_id")
#     passed_data = schema.model_dump()
#     for key, _ in passed_data.items():
#         assert testing_data.get(key) == testing_data.get(key)


