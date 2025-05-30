# Django
from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

# George Forge
from georgeforge.models import DeliverySystem


class SystemChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.friendly


class StoreOrderForm(forms.Form):
    """ """

    notes = forms.CharField(
        label=_("Notes"),
        required=False,
        empty_value="",
        max_length=4096,
        widget=forms.Textarea(attrs={"rows": "5"}),
    )

    delivery = SystemChoiceField(
        queryset=DeliverySystem.objects.filter(enabled=True).all(),
    )


class BulkImportStoreItemsForm(forms.Form):
    """ """

    data = forms.CharField(
        label="CSV Paste",
        empty_value="Item Name,Description,Price,Deposit",
        widget=forms.Textarea(
            attrs={"rows": "15", "placeholder": "Item Name,Description,Price,Deposit"}
        ),
    )
