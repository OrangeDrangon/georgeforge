"""Admin models"""

# Django
from django.contrib import admin

# George Forge
from georgeforge.models import DeliverySystem, ForSale, Order

# Register your models here.


@admin.register(ForSale)
class ForSaleAdmin(admin.ModelAdmin):
    """ """

    list_display = ["eve_type", "description", "deposit", "price"]
    autocomplete_fields = ["eve_type"]


@admin.register(DeliverySystem)
class DeliverySystemAdmin(admin.ModelAdmin):
    """ """

    list_display = ["system", "enabled", "friendly_name"]
    autocomplete_fields = ["system"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """ """

    list_display = ["user", "status", "eve_type", "price", "description", "notes"]
    autocomplete_fields = ["eve_type"]
