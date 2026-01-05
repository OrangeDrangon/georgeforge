"""App Views"""

# Standard Library
import csv
import itertools
import logging
import uuid
from operator import attrgetter

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Alliance Auth (External Libs)
from eveuniverse.models import EveSolarSystem, EveType

# George Forge
from georgeforge.forms import BulkImportStoreItemsForm
from georgeforge.models import DeliverySystem, ForSale, Order
from georgeforge.tasks import (
    send_new_order_webhook,
    send_statusupdate_dm,
)

from . import app_settings

logger = logging.getLogger(__name__)


@login_required
@permission_required("georgeforge.place_order")
def store(request: WSGIRequest) -> HttpResponse:
    """Store view

    :param request: WSGIRequest:

    """

    for_sale = (
        ForSale.objects.select_related("eve_type__eve_group")
        .all()
        .order_by("eve_type__eve_group__name")
    )

    groups = [
        (key, list(l))
        for key, l in itertools.groupby(
            for_sale, key=attrgetter("eve_type.eve_group.name")
        )
    ]
    groups.sort(key=lambda pair: max(entry.price for entry in pair[1]), reverse=True)

    delivery_systems = DeliverySystem.objects.filter(enabled=True).select_related(
        "system"
    )

    context = {"for_sale": groups, "delivery_systems": delivery_systems}

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
@require_POST
def cart_checkout_api(request: WSGIRequest) -> JsonResponse:
    """Cart checkout API endpoint

    :param request: WSGIRequest:
    :return: JsonResponse:

    """
    # Standard Library
    import json

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    items = data.get("items", [])
    deliverysystem_id = data.get("deliverysystem_id")
    notes = data.get("notes", "")

    if not items:
        return JsonResponse({"success": False, "error": "No items in cart"}, status=400)

    if not deliverysystem_id:
        return JsonResponse(
            {"success": False, "error": "Delivery system required"}, status=400
        )

    try:
        deliverysystem = EveSolarSystem.objects.get(id=deliverysystem_id)
    except EveSolarSystem.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Invalid delivery system"}, status=400
        )

    cart_session_id = str(uuid.uuid4())

    items_dict = {}
    for item in items:
        for_sale_id = item.get("for_sale_id")
        quantity = item.get("quantity", 1)

        if quantity < 1:
            return JsonResponse(
                {"success": False, "error": "Minimum quantity 1"}, status=400
            )

        if for_sale_id in items_dict:
            items_dict[for_sale_id] += quantity
        else:
            items_dict[for_sale_id] = quantity

    orders = []

    for for_sale_id, quantity in items_dict.items():
        try:
            for_sale = ForSale.objects.get(id=for_sale_id)
        except ForSale.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": f"Item {for_sale_id} not found"}, status=400
            )

        order = Order.objects.create(
            user=request.user,
            price=for_sale.price,
            totalcost=(for_sale.price * quantity),
            deposit=(for_sale.deposit * quantity),
            eve_type=for_sale.eve_type,
            notes=notes,
            description=for_sale.description,
            status=Order.OrderStatus.PENDING,
            deliverysystem=deliverysystem,
            quantity=quantity,
            cart_session_id=cart_session_id,
        )

        orders.append(order)

    for order in orders:
        send_new_order_webhook(order)
        send_statusupdate_dm(order)

    return JsonResponse(
        {
            "success": True,
            "orders": [
                {
                    "id": order.id,
                    "eve_type": order.eve_type.name,
                    "quantity": order.quantity,
                    "totalcost": float(order.totalcost),
                    "deposit": float(order.deposit),
                }
                for order in orders
            ],
            "cart_session_id": cart_session_id,
        }
    )


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
