"""App Tasks"""

# Standard Library
import json
import logging

# Third Party
import requests

# George Forge
from georgeforge.models import Order

from . import app_settings

logger = logging.getLogger(__name__)

# Create your tasks here
if app_settings.discord_bot_active():
    # Third Party
    from aadiscordbot.cogs.utils.exceptions import NotAuthenticated
    from aadiscordbot.tasks import send_message
    from aadiscordbot.utils.auth import get_discord_user_id
    from discord import Color, Embed


# Shamelessly yoinked from aa-securegroups/tasks.py
def send_discord_dm(user, title, message, color):
    if app_settings.discord_bot_active():
        try:
            e = Embed(title=title, description=message, color=color)
            try:
                send_message(user_id=get_discord_user_id(user), embed=e)
                logger.info(f"sent discord ping to {user} - {message}")
            except NotAuthenticated:
                logger.warning(f"Unable to ping {user} - {message}")

        except Exception as e:
            logger.error(e, exc_info=1)
            pass


def send_statusupdate_dm(order):
    if app_settings.discord_bot_active():
        message = (
            f"Your order for {order.eve_type.name} is now {order.get_status_display()}"
        )
        match order.status:
            case Order.OrderStatus.PENDING:
                c = Color.blue()
            case Order.OrderStatus.AWAITING_DEPOSIT:
                c = Color.purple()
            case Order.OrderStatus.BUILDING:
                c = Color.orange()
            case Order.OrderStatus.AWAITING_FINAL_PAYMENT:
                c = Color.purple()
            case Order.OrderStatus.DELIVERED:
                c = Color.green()
            case Order.OrderStatus.REJECTED:
                c = Color.red()
        send_discord_dm(order.user, f"Order Updated: {order.eve_type.name}", message, c)


def send_update_to_webhook(update):
    web_hook = app_settings.INDUSTRY_ADMIN_WEBHOOK
    if web_hook is not None:
        custom_headers = {"Content-Type": "application/json"}
        r = requests.post(
            web_hook,
            headers=custom_headers,
            data=json.dumps({"content": f"{update}"}),
        )
        logger.debug(f"Got status code {r.status_code} after sending ping")
        try:
            r.raise_for_status()
        except Exception as e:
            logger.error(e, exc_info=1)
