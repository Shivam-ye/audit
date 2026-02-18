from django.core.management.base import BaseCommand
import json
from audit.tasks import process_activity_task
from audit.models import Message


class Command(BaseCommand):
    help = "Process activity payload from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to JSON file"
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run synchronously instead of via Celery"
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        run_sync = options.get("sync", False)

        with open(file_path, "r") as f:
            data = json.load(f)

        # Extract payload items for Message data
        if isinstance(data, dict) and data.get("type") == "audit_logs" and "payload" in data:
            original_payload = data
            payloads = data.get("payload", {})
            items = [payloads] if isinstance(payloads, dict) else payloads
        else:
            original_payload = None
            items = data if isinstance(data, list) else [data]

        # Create Message record for tracking
        db_message = Message.objects.create(
            data={"original_payload": original_payload, "items": items},
            status="processing"
        )

        if run_sync:
            # Run synchronously (for testing)
            from audit.interactors.activity_interactor import ActivityInteractor
            try:
                result = ActivityInteractor.process_payloads(items, original_payload=original_payload)
                db_message.status = "completed"
                db_message.save()
                self.stdout.write(self.style.SUCCESS(f"Task completed successfully. Message ID: {db_message.id}"))
            except Exception as exc:
                db_message.status = "failed"
                db_message.error_message = str(exc)
                db_message.save()
                self.stdout.write(self.style.ERROR(f"Task failed: {exc}"))
        else:
            # Send to Celery for async processing
            process_activity_task.delay(data, message_id=str(db_message.id))
            self.stdout.write(self.style.SUCCESS(f"Task sent to Celery. Message ID: {db_message.id}"))
