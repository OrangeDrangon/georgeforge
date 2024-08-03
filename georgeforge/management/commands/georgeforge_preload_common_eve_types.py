from django.core.management import call_command
from django.core.management.base import BaseCommand

from georgeforge import __title__

# Eve Category IDs
SHIP = 6
STRUCTURES = 63



class Command(BaseCommand):
    help = "Preloads data required for this app from ESI"

    def handle(self, *args, **options):
        call_command(
            "eveuniverse_load_types",
            __title__,
            "--category_id",
            str(SHIP),
            "--category_id",
            str(STRUCTURES),

        )
