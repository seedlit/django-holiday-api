from rest_framework import serializers


class WeatherPreviewRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    start = serializers.DateField()
    end = serializers.DateField()

    def validate(self, attrs):
        if attrs["start"] > attrs["end"]:
            raise serializers.ValidationError("start must be <= end")
        return attrs
