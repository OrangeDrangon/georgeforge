"""App Settings"""

# Django
from django.conf import settings


def discord_bot_active():
    return "aadiscordbot" in settings.INSTALLED_APPS


FORGE_CATEGORIES = getattr(settings, "FORGE_CATEGORIES", [4, 6, 7, 8, 18, 20, 63, 66])

INDUSTRY_ADMIN_WEBHOOK = getattr(settings, "INDUSTRY_ADMIN_WEBHOOK", None)
