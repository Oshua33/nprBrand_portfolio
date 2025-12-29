from uuid import uuid4
from nprOlusolaBe.apps.testimonials.v1 import schemas

def test_create_testimonials_schema():
    testing_data = dict(
        name="test name",
        image_id=uuid4(),
        content="test content",
        is_active=False
    )
    schema = schemas.TestimonialIn(**testing_data)
    assert schema.name == testing_data.get("name")
    assert schema.image_id == testing_data.get("image_id")
    assert schema.content == testing_data.get("content")
    assert schema.is_active == testing_data.get("is_active")
    
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


