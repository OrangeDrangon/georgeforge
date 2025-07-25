# Standard Library
import itertools

# Django
from django.core.management import call_command
from django.core.management.base import BaseCommand

# George Forge
from georgeforge import __title__
from georgeforge.app_settings import FORGE_CATEGORIES


class Command(BaseCommand):
    """ """

    help = "Preloads data required for this app from ESI"

    def handle(self, *args, **options):
        """

        :param *args:
        :param **options:

        """

        categories: list[list[str]] = [
            ["--category_id", str(x)] for x in FORGE_CATEGORIES
        ]

        call_command(
            "eveuniverse_load_types",
            "--noinput",
            __title__,
            *itertools.chain.from_iterable(categories),
        )
        call_command("eveuniverse_load_data", "--noinput", "map")
