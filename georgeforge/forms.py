# Django
from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _

# George Forge
from georgeforge.models import DeliverySystem, Order
from georgeforge.utils.permissioned_forms import PermissionedModelForm


class SystemChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.friendly


class StoreOrderForm(PermissionedModelForm):
    """ """

    class Meta:
        model = Order
        fields = ["notes", "quantity", "on_behalf_of"]
        field_permissions = {"on_behalf_of": "georgeforge.manage_store"}

    delivery = SystemChoiceField(
        label=_("Delivery System"),
        queryset=DeliverySystem.objects.filter(enabled=True).all(),
    )


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
