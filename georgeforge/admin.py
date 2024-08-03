"""Admin models"""
# Standard Library
from typing import Any

from django.contrib import admin  # noqa: F401
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
from django.forms.models import ModelChoiceField
from django.forms.models import ModelMultipleChoiceField
from django.http import HttpRequest
from eveuniverse.models import EveCategory
from eveuniverse.models import EveMarketGroup
from eveuniverse.models import EveType

from georgeforge.models import ForSale
from georgeforge.models import Order
# Django
# Alliance Auth (External Libs)
# George Forge

# Eve Universe

# Register your models here.


@admin.register(ForSale)
class ForSaleAdmin(admin.ModelAdmin):
    """ """

    list_display = ["eve_type", "price", "description"]
    autocomplete_fields = ["eve_type"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """ """

    list_display = ["user", "status", "eve_type", "price", "description", "notes"]
    autocomplete_fields = ["eve_type"]
