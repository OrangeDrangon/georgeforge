"""App Views"""
# Standard Library
import csv
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveType, EveSolarSystem

from georgeforge.forms import BulkImportStoreItemsForm, StoreOrderForm
from georgeforge.models import ForSale, Order, DeliverySystem
# Django
# Alliance Auth (External Libs)
# George Forge

logger = logging.getLogger(__name__)


@login_required
@permission_required("georgeforge.place_order")
def store(request: WSGIRequest) -> HttpResponse:
    """Store view

    :param request: WSGIRequest:

    """

    for_sale = ForSale.objects.select_related().all()

    context = {"for_sale": for_sale}

    return render(request, "georgeforge/views/store.html", context)


@login_required
@permission_required("georgeforge.place_order")
def my_orders(request: WSGIRequest) -> HttpResponse:
    """My Orders view

    :param request: WSGIRequest:

    """

    my_orders = Order.objects.select_related().filter(user=request.user)

    context = {"my_orders": my_orders}

    return render(request, "georgeforge/views/my_orders.html", context)


@login_required
@permission_required("georgeforge.place_order")
def store_order_form(request: WSGIRequest, id: int) -> HttpResponse:
    """Place order for a specific ship

    :param request: WSGIRequest:
    :param id: int:

    """
    for_sale = ForSale.objects.get(id=id)

    if request.method == "POST":
        form = StoreOrderForm(request.POST)

        if form.is_valid():
            notes = form.cleaned_data["notes"]
            system = form.cleaned_data["delivery"].system

            Order.objects.create(
                user=request.user,
                price=for_sale.price,
                eve_type=for_sale.eve_type,
                notes=notes,
                description=for_sale.description,
                status=Order.OrderStatus.PENDING,
                deliverysystem=system,
            )

            messages.success(
                request,
                _("Successfully ordered %(name)s for %(price)s ISK") % {
                    "name": for_sale.eve_type.name,
                    "price": intcomma(for_sale.price)
                },
            )

            return redirect("georgeforge:store")

    context = {"for_sale": for_sale, "form": StoreOrderForm()}

    return render(request, "georgeforge/views/store_order_form.html", context)


@login_required
@permission_required("georgeforge.manage_store")
def all_orders(request: WSGIRequest) -> HttpResponse:
    """Order Management handler/view

    :param request: WSGIRequest:
    
    """
    if request.method == "POST":
        pk = int(request.POST.get('id'))
        if pk < 1:
            messages.error(request,
                message=_("Not a valid order")
            )
        paid = float(request.POST.get('paid').strip(','))
        if float(paid) < 0.00:
            messages.error(request,
                message=_("Negative payment")
            )
        status = int(request.POST.get('status'))
        if status not in dict(Order.OrderStatus.choices).keys():
            messages.error(request,
                message=_("Not a valid status")
            )
        system = EveSolarSystem.objects.get(id=int(request.POST.get('system')))
        Order.objects.filter(pk=pk).update(paid=paid,status=status,deliverysystem=system)


    orders = Order.objects.select_related().all()
    dsystems = []
    for x in DeliverySystem.objects.select_related().all():
        dsystems.append([x.system.id, x.friendly])
    context = {"all_orders": orders, "status": Order.OrderStatus.choices, "dsystems":dsystems}

    return render(request, "georgeforge/views/all_orders.html", context)


@login_required
@permission_required("georgeforge.manage_store")
def bulk_import_form(request: WSGIRequest) -> HttpResponse:
    """

    :param request: WSGIRequest:

    """
    if request.method == "POST":
        form = BulkImportStoreItemsForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data["data"]
            parsed = [
                row for row in csv.DictReader(data.splitlines())
            ]

            ForSale.objects.all().delete()

            had_error = 0

            for item in parsed:
                try:
                    eve_type = EveType.objects.get(name=item["Item Name"])

                    ForSale.objects.create(
                        eve_type=eve_type,
                        description=item["Description"],
                        price=item["Price"],
                        deposit=item["Deposit"]
                    )
                except ObjectDoesNotExist:
                    messages.warning(
                        request,
                        _("%(name)s does not exist and was not added") %
                        {"name": item["Item Name"]},
                    )
                    had_error += 1
                except ValidationError as ex:
                    messages.warning(
                        request,
                        _("%(name)s had a validation error: %(error)s") % {
                            "name": item["Item Name"],
                            "error": ex.message
                        } % ex.params,
                    )
                    had_error += 1

            imported = len(parsed) - had_error

            if imported > 0:
                messages.success(
                    request,
                    _("Imported %(n)s item%(plural)s") % {
                        "n": imported,
                        "plural": pluralize(imported)
                    },
                )

            return redirect("georgeforge:bulk_import_form")

    context = {"form": BulkImportStoreItemsForm()}

    return render(request, "georgeforge/views/bulk_import_form.html", context)


@login_required
@permission_required("georgeforge.manage_store")
def export_offers(request: WSGIRequest) -> HttpResponse:
    """

    :param request: WSGIRequest:

    """
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="auth_forsale.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["Item Name","Description","Price","Deposit"])
    for listing in ForSale.objects.all():
        writer.writerow([listing.eve_type.name, listing.description, listing.price, listing.deposit])
    return response
