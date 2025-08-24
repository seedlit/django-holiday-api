from rest_framework import serializers

from .models import Destination, Schedule, ScheduleItem
from .services.weather import WeatherService


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "latitude", "longitude", "country"]


class ScheduleItemReadSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    weather_summary = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "destination",
            "start_date",
            "end_date",
            "order_index",
            "weather_summary",
        ]

    def get_weather_summary(self, obj):
        try:
            data = WeatherService.fetch(
                lat=obj.destination.latitude,
                lon=obj.destination.longitude,
                start=obj.start_date,
                end=obj.end_date,
            )
            return WeatherService.summarize(data)
        except Exception as e:
            return {"error": str(e)}


class ScheduleReadSerializer(serializers.ModelSerializer):
    items = ScheduleItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = ["id", "name", "created_at", "items"]


class ScheduleItemWriteSerializer(serializers.Serializer):
    destination_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        # we rely on model clean() for date order; here just pass through
        return attrs


class ScheduleWriteSerializer(serializers.ModelSerializer):
    items = ScheduleItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Schedule
        fields = ["id", "name", "items"]

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        schedule = Schedule.objects.create(**validated_data)

        # Create ScheduleItems in posted order
        for idx, item in enumerate(items):
            dest_id = item["destination_id"]
            destination = Destination.objects.get(pk=dest_id)
            ScheduleItem.objects.create(
                schedule=schedule,
                destination=destination,
                start_date=item["start_date"],
                end_date=item["end_date"],
                order_index=idx,
            )
        # Return a read representation (with nested items)
        return schedule

    def to_representation(self, instance):
        return ScheduleReadSerializer(instance).data
