"""
App Models
"""

# Django
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from eveuniverse.models import EveSolarSystem, EveType

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
        validators=[MinValueValidator(1)],
    )

    deposit = models.DecimalField(
        _("Deposit"),
        default=0,
        max_digits=15,
        decimal_places=2,
        help_text=_("Deposit per unit"),
    )


class DeliverySystem(models.Model):
    """A SolarSystem Available for orders to be delivered to"""

    system = models.ForeignKey(
        EveSolarSystem,
        verbose_name=_("Solar System"),
        on_delete=models.CASCADE,
    )

    friendly_name = models.TextField(
        _("Friendly Name"),
        max_length=32,
        default=None,
        null=True,
        blank=True,
    )

    enabled = models.BooleanField(
        default=True,
    )

    @property
    def friendly(self):
        if self.friendly_name:
            return f"{self.system.name} - {self.friendly_name}"
        return self.system.name


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
        _("Price per unit"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Cost per unit"),
    )

    totalcost = models.DecimalField(
        _("Total Order cost"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Total Order cost"),
    )

    deposit = models.DecimalField(
        _("Deposit required per unit"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Deposit required per unit"),
    )

    paid = models.DecimalField(
        _("Amount Paid"),
        default=0,
        max_digits=15,
        decimal_places=2,
        help_text=_("Amount paid"),
    )

    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_("EVE Type"),
        on_delete=models.CASCADE,
        limit_choices_to={"published": 1},
    )

    quantity = models.IntegerField(
        _("Quantity"),
        default=1,
        validators=[MinValueValidator(1)],
    )

    notes = models.TextField(
        _("Notes"),
        blank=True,
        max_length=4096,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
        max_length=4096,
    )

    deliverysystem = models.ForeignKey(
        EveSolarSystem,
        verbose_name=_("Delivery System"),
        on_delete=models.CASCADE,
    )

    status = models.IntegerField(_("Status"), choices=OrderStatus.choices)
