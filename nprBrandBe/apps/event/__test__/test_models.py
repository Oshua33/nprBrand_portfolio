from uuid import uuid4
from nprOlusolaBe.apps.event.models import Event
from datetime import datetime, timedelta

def test_create_event_model():
    # Define start and end times/dates
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=1)
    start_time = datetime.now().time()
    end_time = (datetime.now() + timedelta(hours=2)).time()
    
    

    # Create Event instance with all required fields
    new_event = Event(
        title="Test Event",
        description="This is a test event.",
        image=uuid4(),
        is_publish=True,
        category=uuid4(),
        label=uuid4(),
        start_date=start_date,
        end_date=end_date,
        start_time=start_time,
        end_time=end_time,
        location="Test Location"
    )


    assert new_event.title == "Test Event"
    assert new_event.location == "Test Location"
