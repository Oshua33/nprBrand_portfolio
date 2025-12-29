from nprOlusolaBe.apps.label.models import Label


def test_create_label_model():
    testing_data = dict(
        title="Test Label Title",
        type="Test Type"
    )
    new_label = Label(
        title=testing_data.get("title"),
        type=testing_data.get("type"),
        
    )

    assert new_label.title == testing_data.get("title")
    assert new_label.type == testing_data.get("type")

