"""Admin models"""

# Standard Library
from typing import Any

# Django
from django.contrib import admin  # noqa: F401
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.http import HttpRequest

# Alliance Auth (External Libs)
from eveuniverse.models import EveCategory, EveMarketGroup, EveType

# George Forge
from georgeforge.models import ForSale, Order

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
