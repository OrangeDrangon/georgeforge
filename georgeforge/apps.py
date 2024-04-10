"""App Configuration"""

# Django
from django.apps import AppConfig

# George Forge
from georgeforge import __version__


class GeorgeForgeConfig(AppConfig):
    """App Config"""

    name = "georgeforge"
    label = "georgeforge"
    verbose_name = f"George Forge v{__version__}"
