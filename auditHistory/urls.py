
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
#     path("update", update_audit),
#     path("history/<str:service>", get_history),
]
