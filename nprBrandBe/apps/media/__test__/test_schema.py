from uuid import uuid4
from nprOlusolaBe.apps.media.v1 import schemas

def test_create_media_schema():
    testing_data = dict(
        url="test url",
        type="test type",
        file_name="test file"
    )
    schema = schemas.MediaIn(**testing_data)
    assert schema.url == testing_data.get("url")
    assert schema.type == testing_data.get("type")
    assert schema.file_name == testing_data.get("file_name")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


