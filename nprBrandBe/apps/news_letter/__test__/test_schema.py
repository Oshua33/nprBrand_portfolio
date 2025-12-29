import email
from uuid import uuid4
from nprOlusolaBe.apps.news_letter.v1 import schemas

def test_create_news_letter_schema():
    testing_data = dict(
        email="testemail@gmail.com",
    )
    schema = schemas.NewsLetterIn(**testing_data)
    assert schema.email == testing_data.get("email")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


