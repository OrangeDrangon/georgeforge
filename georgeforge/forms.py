# Django
from django import forms
from django.utils.translation import gettext_lazy as _


class BulkImportStoreItemsForm(forms.Form):
    """ """

    data = forms.CharField(
        label=_("CSV Paste"),
        empty_value=_("Item Name,Description,Price,Deposit"),
        widget=forms.Textarea(
            attrs={
                "rows": "15",
                "placeholder": _("Item Name,Description,Price,Deposit"),
            }
        ),
    )
