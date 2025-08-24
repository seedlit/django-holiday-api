from rest_framework import serializers


class GeocodeRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200)
