from django.urls import path

from .views import (DestinationListCreateView, GeocodeView, ScheduleCreateView,
                    ScheduleDetailView, WeatherPreviewView)

urlpatterns = [
    path("destinations/", DestinationListCreateView.as_view(), name="destinations"),
    path("schedules/", ScheduleCreateView.as_view(), name="schedules-create"),
    path("schedules/<int:pk>/", ScheduleDetailView.as_view(), name="schedules-detail"),
    path("geocode/", GeocodeView.as_view(), name="geocode"),
    path("weather/preview", WeatherPreviewView.as_view(), name="weather-preview"),
]
