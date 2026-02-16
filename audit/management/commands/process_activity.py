from django.core.management.base import BaseCommand
import json
from audit.tasks import process_activity_task


class Command(BaseCommand):
    help = "Process activity payload from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to JSON file"
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        with open(file_path, "r") as f:
            data = json.load(f)

        process_activity_task.delay(data)

        self.stdout.write(self.style.SUCCESS("Task sent to Celery"))
