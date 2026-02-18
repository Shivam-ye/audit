from django.db import models
import uuid
from django.utils import timezone


class CoreMessageModel(models.Model):
    """
    Base model for message tracking - inspired by tools_box.workers.model.CoreMessageModel
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=50, default="pending")
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        abstract = True


class Message(CoreMessageModel):
    """
    Message model for audit log processing queue.
    Stores the payload data for async processing.
    """
    class Meta(CoreMessageModel.Meta):
        db_table = 'audit_message'
        app_label = 'audit'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        
    def __str__(self):
        return f"Message {self.id} - {self.status}"

