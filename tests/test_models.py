from datetime import date

import pytest
from django.core.exceptions import ValidationError

from trips.models import Destination, Schedule, ScheduleItem

pytestmark = pytest.mark.django_db


def test_create_destination_and_schedule():
    dest = Destination.objects.create(
        name="Berlin", latitude=52.52, longitude=13.405, country="Germany"
    )
    sched = Schedule.objects.create(name="Euro Hop")
    item = ScheduleItem.objects.create(
        schedule=sched,
        destination=dest,
        start_date=date(2025, 6, 10),
        end_date=date(2025, 6, 12),
        order_index=0,
    )
    assert dest.pk is not None
    assert sched.pk is not None
    assert item.pk is not None
    assert str(item).startswith("Berlin")


def test_schedule_item_rejects_end_before_start():
    dest = Destination.objects.create(name="Rome", latitude=41.9028, longitude=12.4964)
    sched = Schedule.objects.create()
    with pytest.raises(ValidationError) as excinfo:
        ScheduleItem.objects.create(
            schedule=sched,
            destination=dest,
            start_date=date(2025, 7, 5),
            end_date=date(2025, 7, 4),  # invalid
            order_index=0,
        )
    # Ensure the error is specifically on end_date
    assert "end_date" in excinfo.value.message_dict


def test_destination_lat_lon_validators():
    with pytest.raises(ValidationError):
        Destination(name="Nowhere", latitude=200.0, longitude=0.0).full_clean()
    with pytest.raises(ValidationError):
        Destination(name="AlsoNowhere", latitude=0.0, longitude=-200.0).full_clean()
