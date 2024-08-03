"""
App Models
"""

# Eve Universe
from eveuniverse.models import EveType, EveMarketGroup

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    """
    An item for sale
    """

    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_("EVE Type"),
        on_delete=models.CASCADE,
        limit_choices_to={"published": 1, "eve_market_group__isnull": False},
    )

    description = models.TextField(_("Description"), blank=True)

    price = models.DecimalField(
        _("Price"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Cost per unit"),
    )
