"""App Tasks"""

# Standard Library
import json
import logging

# Third Party
import requests
from celery import shared_task

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

        e = Embed(
            title=f"Order #{order.pk} Status: {order.get_status_display()}", color=c
        )
        e.add_field(name="Item", value=order.eve_type.name, inline=True)
        e.add_field(name="Quantity", value=str(order.quantity), inline=True)
        e.add_field(name="Price per Unit", value=f"{order.price:,.2f} ISK", inline=True)
        e.add_field(name="Total Cost", value=f"{order.totalcost:,.2f} ISK", inline=True)
        e.add_field(name="Deposit", value=f"{order.deposit:,.2f} ISK", inline=True)
        e.add_field(
            name="Delivery System", value=order.deliverysystem.name, inline=True
        )
        if order.estimated_delivery_date:
            e.add_field(
                name="Estimated Delivery",
                value=order.estimated_delivery_date,
                inline=True,
            )
        if order.description:
            e.add_field(name="Description", value=order.description, inline=False)
        if order.notes:
            e.add_field(name="Notes", value=order.notes, inline=False)

        try:
            send_message(user_id=get_discord_user_id(order.user), embed=e)
            logger.info(
                f"sent discord ping to {order.user} - order #{order.pk} status updated to {order.get_status_display()}"
            )
        except NotAuthenticated:
            logger.warning(
                f"Unable to ping {order.user} - order #{order.pk} status updated"
            )


def send_deliverydateupdate_dm(order):
    if app_settings.discord_bot_active():
        e = Embed(title=f"Order #{order.pk} Delivery Date Updated", color=Color.blue())

        if order.estimated_delivery_date:
            e.add_field(
                name="New Estimated Delivery",
                value=order.estimated_delivery_date,
                inline=False,
            )
        else:
            e.add_field(name="Estimated Delivery", value="Cleared", inline=False)

        e.add_field(name="Item", value=order.eve_type.name, inline=True)
        e.add_field(name="Quantity", value=str(order.quantity), inline=True)
        e.add_field(name="Price per Unit", value=f"{order.price:,.2f} ISK", inline=True)
        e.add_field(name="Total Cost", value=f"{order.totalcost:,.2f} ISK", inline=True)
        e.add_field(name="Deposit", value=f"{order.deposit:,.2f} ISK", inline=True)
        e.add_field(
            name="Delivery System", value=order.deliverysystem.name, inline=True
        )
        e.add_field(name="Status", value=order.get_status_display(), inline=True)
        if order.description:
            e.add_field(name="Description", value=order.description, inline=False)
        if order.notes:
            e.add_field(name="Notes", value=order.notes, inline=False)

        try:
            send_message(user_id=get_discord_user_id(order.user), embed=e)
            logger.info(
                f"sent discord ping to {order.user} - order #{order.pk} delivery date updated"
            )
        except NotAuthenticated:
            logger.warning(
                f"Unable to ping {order.user} - order #{order.pk} delivery date updated"
            )


@shared_task
def send_update_to_webhook(content=None, embed=None):
    web_hook = app_settings.INDUSTRY_ADMIN_WEBHOOK
    if web_hook is not None:
        custom_headers = {"Content-Type": "application/json"}
        payload = {}
        if embed:
            payload["embeds"] = [embed]
        if content:
            payload["content"] = content
        elif not embed:
            payload["content"] = "New order update"
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


@shared_task
def send_new_order_webhook(order_pk):
    if not app_settings.webhook_available():
        return

    order = Order.objects.get(pk=order_pk)
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
    if order.description:
        embed.add_field(name="Description", value=order.description, inline=False)
    if order.notes:
        embed.add_field(name="Notes", value=order.notes, inline=False)

    content = None
    role_id = app_settings.INDUSTRY_ADMIN_WEBHOOK_ROLE_ID
    if role_id:
        content = f"<@&{role_id}>"

    send_update_to_webhook.delay(content=content, embed=embed.to_dict())
