from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityStreamViewSet

router = DefaultRouter()
router.register(r'activity-stream', ActivityStreamViewSet, basename='activity-stream')

urlpatterns = [
    path('', include(router.urls)),
]
