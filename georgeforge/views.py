"""App Views"""

# Standard Library
import csv
import logging

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from eveuniverse.models import EveSolarSystem, EveType

# George Forge
from georgeforge.forms import BulkImportStoreItemsForm, StoreOrderForm
from georgeforge.models import DeliverySystem, ForSale, Order
from georgeforge.tasks import (
    send_statusupdate_dm,
    send_update_to_webhook,
)

from . import app_settings

logger = logging.getLogger(__name__)


@login_required
@permission_required("georgeforge.place_order")
def store(request: WSGIRequest) -> HttpResponse:
    """Store view

    :param request: WSGIRequest:

    """

    for_sale = ForSale.objects.select_related().all().order_by("eve_type__eve_group_id")

    context = {"for_sale": for_sale}

    return render(request, "georgeforge/views/store.html", context)


@login_required
@permission_required("georgeforge.place_order")
def my_orders(request: WSGIRequest) -> HttpResponse:
    """My Orders view

    :param request: WSGIRequest:

    """

    my_orders = (
        Order.objects.select_related()
        .filter(user=request.user, status__lt=Order.OrderStatus.DELIVERED)
        .order_by("-id")
    )
    done_orders = (
        Order.objects.select_related()
        .filter(user=request.user, status__gte=Order.OrderStatus.DELIVERED)
        .order_by("-id")
    )

    context = {"my_orders": my_orders, "done_orders": done_orders}

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
            quantity = form.cleaned_data["quantity"]

            # IDK if we need to do this but it feels better
            on_behalf_of = None
            if request.user.has_perm("georgeforge.manage_store"):
                on_behalf_of = form.cleaned_data["on_behalf_of"]

            if quantity < 1:
                messages.error(request, _("Minimum quantity 1"))
                return redirect("georgeforge:store")

            order = Order.objects.create(
                user=request.user,
                price=for_sale.price,
                totalcost=(for_sale.price * quantity),
                deposit=(for_sale.deposit * quantity),
                eve_type=for_sale.eve_type,
                notes=notes,
                description=for_sale.description,
                status=Order.OrderStatus.PENDING,
                deliverysystem=system,
                quantity=quantity,
                on_behalf_of=on_behalf_of,
            )

            send_update_to_webhook(
                f"<@&610206372079861780> New Ship Order submitted! Ship Hull: {quantity} x {for_sale.eve_type.name}, Submitted By: {request.user.profile.main_character.character_name}"
            )

            send_statusupdate_dm(order)

            messages.success(
                request,
                _("Successfully ordered %(qty)d x %(name)s for %(price)s ISK")
                % {
                    "qty": quantity,
                    "name": for_sale.eve_type.name,
                    "price": intcomma(for_sale.price * quantity),
                },
            )

            return redirect("georgeforge:store")

    context = {"for_sale": for_sale, "form": StoreOrderForm(for_user=request.user)}

    return render(request, "georgeforge/views/store_order_form.html", context)


@login_required
@permission_required("georgeforge.manage_store")
def all_orders(request: WSGIRequest) -> HttpResponse:
    """Order Management handler/view

    :param request: WSGIRequest:

    """
    if request.method == "POST":
        id = int(request.POST.get("id"))
        paid = float(request.POST.get("paid").strip(","))
        status = int(request.POST.get("status"))
        quantity = int(request.POST.get("quantity"))

        if id >= 1:
            try:
                order = Order.objects.filter(id=id).get()
            except IndexError:
                messages.error(request, message=_("Not a valid order"))
                return redirect("georgeforge:all_orders")

        if float(paid) < 0.00:
            messages.error(request, message=_("Negative payment"))
            return redirect("georgeforge:all_orders")

        if status not in dict(Order.OrderStatus.choices).keys():
            messages.error(request, message=_("Not a valid status"))
            return redirect("georgeforge:all_orders")

        if quantity < 1:
            messages.error(request, message=_("Cannot order 0 of things!"))
            return redirect("georgeforge:all_orders")

        deliverysystem = EveSolarSystem.objects.get(id=int(request.POST.get("system")))
        order.paid = paid
        old_status = order.status
        order.status = status
        order.deliverysystem = deliverysystem
        order.quantity = quantity
        order.totalcost = order.price * quantity
        order.save()

        messages.success(request, f"Order ID {id} updated!")

        if order.status != old_status:
            send_statusupdate_dm(order)

        return redirect("georgeforge:all_orders")

    orders = (
        Order.objects.select_related()
        .filter(status__lt=Order.OrderStatus.DELIVERED)
        .order_by("-id")
    )
    done_orders = (
        Order.objects.select_related()
        .filter(status__gte=Order.OrderStatus.DELIVERED)
        .order_by("-id")
    )
    dsystems = []
    for x in DeliverySystem.objects.select_related().all():
        dsystems.append([x.system.id, x.friendly])
    context = {
        "all_orders": orders,
        "done_orders": done_orders,
        "status": Order.OrderStatus.choices,
        "dsystems": dsystems,
    }

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
                row
                for row in csv.DictReader(
                    data.splitlines(),
                    fieldnames=["Item Name", "Description", "Price", "Deposit"],
                )
            ]
            ForSale.objects.all().delete()

            had_error = 0

            for item in parsed:
                try:
                    eve_type = EveType.objects.filter(
                        eve_group__eve_category_id__in=app_settings.FORGE_CATEGORIES
                    ).get(name=item["Item Name"])

                    ForSale.objects.create(
                        eve_type=eve_type,
                        description=item["Description"],
                        price=item["Price"],
                        deposit=item["Deposit"],
                    )
                except ObjectDoesNotExist:
                    messages.warning(
                        request,
                        _("%(name)s does not exist and was not added")
                        % {"name": item["Item Name"]},
                    )
                    had_error += 1
                except ValidationError as ex:
                    messages.warning(
                        request,
                        _("%(name)s had a validation error: %(error)s")
                        % {"name": item["Item Name"], "error": ex.message}
                        % ex.params,
                    )
                    had_error += 1

            imported = len(parsed) - had_error

            if imported > 0:
                messages.success(
                    request,
                    _("Imported %(n)s item%(plural)s")
                    % {"n": imported, "plural": pluralize(imported)},
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
    for listing in ForSale.objects.all():
        writer.writerow(
            [listing.eve_type.name, listing.description, listing.price, listing.deposit]
        )
    return response
