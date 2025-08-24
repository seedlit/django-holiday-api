from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Destination, Schedule
from .serializers import (
    DestinationSerializer,
    ScheduleReadSerializer,
    ScheduleWriteSerializer,
)
from .serializers_geocode import GeocodeRequestSerializer
from .serializers_weather import WeatherPreviewRequestSerializer
from .services.geocoding import GeocodingService
from .services.weather import WeatherService


class DestinationListCreateView(generics.ListCreateAPIView):
    serializer_class = DestinationSerializer

    def get_queryset(self):
        qs = Destination.objects.all().order_by("id")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class ScheduleCreateView(generics.CreateAPIView):
    serializer_class = ScheduleWriteSerializer
    queryset = Schedule.objects.all()


class ScheduleDetailView(generics.RetrieveAPIView):
    serializer_class = ScheduleReadSerializer
    queryset = Schedule.objects.prefetch_related("items__destination").all()


class GeocodeView(APIView):
    throttle_scope = "geocode"

    def post(self, request):
        serializer = GeocodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]

        result = GeocodingService.geocode(query)
        if not result:
            return Response({"detail": "No results"}, status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class WeatherPreviewView(APIView):
    throttle_scope = "weather"

    def get(self, request):
        serializer = WeatherPreviewRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        data = WeatherService.fetch(
            lat=params["lat"],
            lon=params["lon"],
            start=params["start"],
            end=params["end"],
        )
        summary = WeatherService.summarize(data)
        return Response({"summary": summary, "raw": data.get("daily", {})})
