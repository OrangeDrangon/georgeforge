# Django
from django import forms
from django.utils.translation import gettext_lazy as _

from georgeforge.models import Order


class StoreOrderForm(forms.Form):
    """ """
    notes = forms.CharField(
        label=_("Notes"),
        required=False,
        empty_value="",
        max_length=4096,
        widget=forms.Textarea(attrs={"rows": "5"}),
    )


class BulkImportStoreItemsForm(forms.Form):
    """ """
    data = forms.CharField(
        label="CSV Paste",
        empty_value="Item Name,Description,Price,Deposit",
        widget=forms.Textarea(attrs={
            "rows": "15",
            "placeholder": "Item Name,Description,Price,Deposit"
        }),
    )
