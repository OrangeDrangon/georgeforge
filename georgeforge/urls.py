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
    path("my_orders", views.my_orders, name="my_orders"),
    path("bulk_import_form", views.bulk_import_form, name="bulk_import_form"),
]
