from django.db import models
import uuid
from django.utils import timezone


class AuditHistory(models.Model):
    resource_type     = models.CharField(max_length=100)
    resource_id       = models.CharField(max_length=255)
    version           = models.PositiveIntegerField()
    operation         = models.CharField(max_length=20)  
    actor_id          = models.CharField(max_length=255, blank=True, null=True)
    actor             = models.JSONField(default=dict, blank=True)
    timestamp         = models.DateTimeField(default=timezone.now)
    event_id          = models.UUIDField(default=uuid.uuid4, editable=False)
    changes           = models.JSONField(default=dict)
    summary           = models.TextField(blank=True)
    full_fields_after = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['resource_type', 'resource_id', '-version']),
            models.Index(fields=['-timestamp']),
        ]
        unique_together = [['resource_type', 'resource_id', 'version']]
        ordering = ['-timestamp']
        db_table = 'audit_audithistory' 

    def __str__(self):
        return f"{self.resource_type} {self.resource_id} v{self.version}"