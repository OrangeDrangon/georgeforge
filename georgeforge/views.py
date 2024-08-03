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
from eveuniverse.models import EveType

# George Forge
from georgeforge.forms import BulkImportStoreItemsForm, StoreOrderForm
from georgeforge.models import ForSale, Order

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
def store_order_form(request: WSGIRequest, id: int) -> HttpResponse:
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

            return redirect("georgeforge:store")

    context = {"for_sale": for_sale, "form": StoreOrderForm()}

    return render(request, "georgeforge/views/store_order_form.html", context)


@login_required
@permission_required("georgeforge.manage_store")
def bulk_import_form(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        form = BulkImportStoreItemsForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data["data"]
            parsed = [
                row
                for row in csv.DictReader(
                    data.splitlines(), fieldnames=("name", "price", "description")
                )
            ]

            ForSale.objects.all().delete()

            had_error = 0

            for item in parsed:
                try:
                    eve_type = EveType.objects.get(name=item["name"])

                    ForSale.objects.create(
                        eve_type=eve_type,
                        description=item["description"],
                        price=item["price"],
                    )
                except ObjectDoesNotExist:
                    messages.warning(
                        request,
                        _("%(name)s does not exist and was not added")
                        % {"name": item["name"]},
                    )
                    had_error += 1
                except ValidationError as ex:
                    messages.warning(
                        request,
                        _("%(name)s had a validation error: %(error)s")
                        % {"name": item["name"], "error": ex.message}
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
