"""App Settings"""

# Django
from django.conf import settings


def discord_bot_active():
    return "aadiscordbot" in settings.INSTALLED_APPS

FORGE_MARKET_GROUPS = getattr(settings, "FORGE_MARKET_GROUPS", [4,6,7,8,18,20,63,66])

INDUSTRY_ADMIN_WEBHOOK = getattr(settings, "INDUSTRY_ADMIN_WEBHOOK", None)
