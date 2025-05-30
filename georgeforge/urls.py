"""App URLs"""
# Django
from django.urls import path

from georgeforge import views
# George Forge

app_name: str = "georgeforge"

urlpatterns = [
    path("store", views.store, name="store"),
    path("store/order/<int:id>",
         views.store_order_form,
         name="store_order_form"),
    path("orders", views.my_orders, name="my_orders"),
    path("orders/all", views.all_orders, name="all_orders"),
    path("bulk_import_form", views.bulk_import_form, name="bulk_import_form"),
    path("bulk_import_form/export", views.export_offers, name="export_offers"),
]
