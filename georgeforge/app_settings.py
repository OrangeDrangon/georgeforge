"""App Settings"""

# Django
from django.conf import settings


def discord_bot_active():
    return "aadiscordbot" in settings.INSTALLED_APPS


INDUSTRY_ADMIN_WEBHOOK = getattr(settings, "INDUSTRY_ADMIN_WEBHOOK", None)
