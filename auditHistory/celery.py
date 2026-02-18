import os 
from celery import Celery 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auditHistory.settings")

app = Celery("auditHistory")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in the audit app
app.autodiscover_tasks(['audit'])
