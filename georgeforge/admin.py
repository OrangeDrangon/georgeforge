"""Admin models"""

from typing import Any

# Eve Universe
from eveuniverse.models import EveType, EveCategory, EveMarketGroup

# Django
from django.contrib import admin  # noqa: F401
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.http import HttpRequest

# George Forge
from georgeforge.models import ForSale

# Register your models here.


@admin.register(ForSale)
class ForSaleAdmin(admin.ModelAdmin):
    list_display = ["eve_type", "price", "description"]
    autocomplete_fields = ["eve_type"]
