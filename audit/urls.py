# audit/urls.py
from django.urls import path
from .views import activity_stream

urlpatterns = [
    path("activity-stream/", activity_stream, name="activity_stream"),
]
