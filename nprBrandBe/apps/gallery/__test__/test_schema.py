from uuid import uuid4
from nprOlusolaBe.apps.gallery.v1 import schemas

def test_create_gallery_schema():
    testing_data = dict(
        title="test title",
        image_id=uuid4(),
        label_id=uuid4()
    )
    schema = schemas.GalleryIn(**testing_data)
    assert schema.title == testing_data.get("title")
    assert schema.image_id == testing_data.get("image_id")
    assert schema.label_id == testing_data.get("label_id")
    passed_data = schema.model_dump()
    for key, _ in passed_data.items():
        assert testing_data.get(key) == testing_data.get(key)


