"""App URLs"""

# Django
from django.urls import path

# George Forge
from georgeforge import views

app_name: str = "georgeforge"

urlpatterns = [
    path("", views.store, name="store"),
    path("order/<int:id>", views.order, name="order")
]
