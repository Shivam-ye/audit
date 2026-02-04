from django.urls import path
from .views import compare_json

urlpatterns = [
    path("compare/", compare_json),
]
