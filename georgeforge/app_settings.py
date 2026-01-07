"""App Settings"""

# Django
from django.conf import settings


def discord_bot_active():
    return "aadiscordbot" in settings.INSTALLED_APPS


def webhook_available():
    try:
        # Third Party
        import discord

        return discord is not None
    except ImportError:
        return False


FORGE_CATEGORIES = getattr(settings, "FORGE_CATEGORIES", [4, 6, 7, 8, 18, 20, 63, 66])

INDUSTRY_ADMIN_WEBHOOK = getattr(settings, "INDUSTRY_ADMIN_WEBHOOK", None)

INDUSTRY_ADMIN_WEBHOOK_ROLE_ID = getattr(
    settings, "INDUSTRY_ADMIN_WEBHOOK_ROLE_ID", None
)

ORDER_DEPOSIT_INSTRUCTIONS = getattr(settings, "ORDER_DEPOSIT_INSTRUCTIONS", None)
