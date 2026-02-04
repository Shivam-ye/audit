from django.urls import path
from .views import update_audit, get_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path("update", update_audit),
    path("history/<str:service>", get_history),
]
