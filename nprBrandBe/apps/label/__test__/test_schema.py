from uuid import uuid4
from nprOlusolaBe.apps.label.v1 import schemas

def test_create_label_schema():
    testing_data = dict(
        title="test title",
        type="test type"
    )
    schema = schemas.LabelIn(**testing_data)
    assert schema.title == testing_data.get("title")
    assert schema.type == testing_data.get("type")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


