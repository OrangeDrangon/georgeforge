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
if app_settings.webhook_available():
    # Third Party
    from discord import Color, Embed

if app_settings.discord_bot_active():
    # Third Party
    from aadiscordbot.cogs.utils.exceptions import NotAuthenticated
    from aadiscordbot.tasks import send_message
    from aadiscordbot.utils.auth import get_discord_user_id


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
            case Order.OrderStatus.BUILDING_PARTS:
                c = Color.orange()
            case Order.OrderStatus.BUILDING_HULL:
                c = Color.orange()
            case Order.OrderStatus.AWAITING_FINAL_PAYMENT:
                c = Color.purple()
            case Order.OrderStatus.DELIVERED:
                c = Color.green()
            case Order.OrderStatus.REJECTED:
                c = Color.red()
        send_discord_dm(order.user, f"Order Updated: {order.eve_type.name}", message, c)


def send_update_to_webhook(content=None, embed=None):
    web_hook = app_settings.INDUSTRY_ADMIN_WEBHOOK
    if web_hook is not None:
        custom_headers = {"Content-Type": "application/json"}
        payload = {}
        if embed:
            payload["embeds"] = [embed]
        else:
            payload["content"] = content or "New order update"
        r = requests.post(
            web_hook,
            headers=custom_headers,
            data=json.dumps(payload),
        )
        logger.debug(f"Got status code {r.status_code} after sending ping")
        try:
            r.raise_for_status()
        except Exception as e:
            logger.error(e, exc_info=1)


def send_new_order_webhook(order):
    if not app_settings.webhook_available():
        return

    embed = Embed(
        title=f"New Ship Order: {order.quantity} x {order.eve_type.name}",
        color=Color.blue(),
    )
    embed.add_field(
        name="Purchaser",
        value=order.user.profile.main_character.character_name,
        inline=True,
    )
    embed.add_field(name="Quantity", value=str(order.quantity), inline=True)
    embed.add_field(
        name="Price per Unit",
        value=f"{order.price:,.2f} ISK",
        inline=True,
    )
    embed.add_field(
        name="Total Cost",
        value=f"{order.totalcost:,.2f} ISK",
        inline=True,
    )
    embed.add_field(name="Deposit", value=f"{order.deposit:,.2f} ISK", inline=True)
    embed.add_field(
        name="Delivery System", value=order.deliverysystem.name, inline=True
    )
    embed.add_field(name="Status", value=order.get_status_display(), inline=True)
    if order.on_behalf_of:
        embed.add_field(name="On Behalf Of", value=order.on_behalf_of, inline=True)
    if order.description:
        embed.add_field(name="Description", value=order.description, inline=False)
    if order.notes:
        embed.add_field(name="Notes", value=order.notes, inline=False)
    send_update_to_webhook(embed=embed.to_dict())
