"""App Views"""

import logging

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


# George Forge
from georgeforge.models import ForSale, Order
from georgeforge.forms import StoreOrderForm

logger = logging.getLogger(__name__)


@login_required
@permission_required("georgeforge.place_order")
def store(request: WSGIRequest) -> HttpResponse:
    """
    Store view
    """

    for_sale = ForSale.objects.select_related().all()

    context = {"for_sale": for_sale}

    return render(request, "georgeforge/views/store.html", context)


@login_required
@permission_required("georgeforge.place_order")
def order(request: WSGIRequest, id: int) -> HttpResponse:
    """
    Place order for a specific ship
    """
    for_sale = ForSale.objects.get(id=id)

    if request.method == "POST":
        form = StoreOrderForm(request.POST)

        if form.is_valid():
            notes = form.cleaned_data["notes"]

            Order.objects.create(
                user=request.user,
                price=for_sale.price,
                eve_type=for_sale.eve_type,
                notes=notes,
                description=for_sale.description,
                status=Order.OrderStatus.PENDING,
            )

            messages.success(
                request,
                _("Successfully ordered %(name)s for %(price)s ISK")
                % {"name": for_sale.eve_type.name, "price": intcomma(for_sale.price)},
            )

            return HttpResponseRedirect("/georgeforge")

    else:
        form = StoreOrderForm()

    context = {"for_sale": for_sale, "form": form}

    return render(request, "georgeforge/views/store_order_form.html", context)
