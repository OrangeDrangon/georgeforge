"""App URLs"""

# Django
from django.urls import path

# George Forge
from georgeforge import views

app_name: str = "georgeforge"

urlpatterns = [
    path("store", views.store, name="store"),
    path("orders", views.my_orders, name="my_orders"),
    path("orders/all", views.all_orders, name="all_orders"),
    path("api/cart/checkout", views.cart_checkout_api, name="cart_checkout_api"),
    path("bulk_import_form", views.bulk_import_form, name="bulk_import_form"),
    path("bulk_import_form/export", views.export_offers, name="export_offers"),
]
