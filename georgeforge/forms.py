# Django
from django import forms
from django.utils.translation import gettext_lazy as _


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
        label="Data",
        empty_value="",
        widget=forms.Textarea(attrs={
            "rows": "5",
            "placeholder": "Item Name,Price,Description"
        }),
    )
