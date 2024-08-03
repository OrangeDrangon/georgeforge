"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

# George Forge
from georgeforge.models import ForSale


@login_required
@permission_required("georgeforge.place_order")
def index(request: WSGIRequest) -> HttpResponse:
    """
    Index view
    :param request
    """

    context = {"text": "Hello, World!"}

    return render(request, "georgeforge/index.html", context)


@login_required
@permission_required("georgeforge.place_order")
def store(request: WSGIRequest) -> HttpResponse:
    """
    Store view
    """

    for_sale = ForSale.objects.select_related().all()

    context = {"for_sale": for_sale}

    return render(request, "georgeforge/views/store.html", context)
