"""Template tags for georgeforge"""

# Django
from django import template

# George Forge
from georgeforge import app_settings

register = template.Library()


@register.filter
def has_discord_linked(user):
    """Check if user has discord linked using get_discord_user_id"""
    if not app_settings.discord_bot_active():
        return True

    try:
        # Third Party
        from aadiscordbot.cogs.utils.exceptions import NotAuthenticated
        from aadiscordbot.utils.auth import get_discord_user_id

        get_discord_user_id(user)
        return True
    except NotAuthenticated:
        return False
    except ImportError:
        return True
