import email
from uuid import uuid4
from nprOlusolaBe.apps.reviews.v1 import schemas

def test_create_review_schema():
    testing_data = dict(
        name="test name",
        email="testemail@gmail.com",
        content="test content",
        
    )
    schema = schemas.ReviewIn(**testing_data)
    assert schema.name == testing_data.get("name")
    assert schema.content == testing_data.get("content")
    assert schema.email == testing_data.get("email")
    
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


