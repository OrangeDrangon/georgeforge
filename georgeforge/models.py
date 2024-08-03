"""
App Models
"""
# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveMarketGroup
from eveuniverse.models import EveType
# Alliance Auth (External Libs)

# Eve Universe


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (
            ("place_order", "Can place an order"),
            ("manage_store", "Can manage the store"),
        )


class ForSale(models.Model):
    """An item for sale"""

    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_("EVE Type"),
        on_delete=models.CASCADE,
        limit_choices_to={"published": 1},
    )

    description = models.TextField(
        _("Description"),
        blank=True,
        max_length=4096,
    )

    price = models.DecimalField(
        _("Price"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Cost per unit"),
    )


class Order(models.Model):
    """An order from a user"""

    class OrderStatus(models.IntegerChoices):
        """ """

        PENDING = 10, _("Pending")
        AWAITING_DEPOSIT = 20, _("Awaiting Deposit")
        BUILDING = 30, _("Building")
        AWAITING_FINAL_PAYMENT = 40, _("Awaiting Final Payment")
        DELIVERED = 50, _("Delivered")
        REJECTED = 60, _("Rejected")

    user = models.ForeignKey(
        User,
        verbose_name=_("Purchaser"),
        on_delete=models.RESTRICT,
    )

    price = models.DecimalField(
        _("Price"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Cost per unit"),
    )

    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_("EVE Type"),
        on_delete=models.CASCADE,
        limit_choices_to={"published": 1},
    )

    notes = models.TextField(
        _("Notes"),
        max_length=4096,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
        max_length=4096,
    )

    status = models.IntegerField(_("Status"), choices=OrderStatus.choices)
