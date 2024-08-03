from django import forms


class StoreOrderForm(forms.Form):
    notes = forms.CharField(
        label="Notes",
        required=False,
        empty_value="",
        max_length=4096,
        widget=forms.Textarea(attrs={"rows": "5"}),
    )
