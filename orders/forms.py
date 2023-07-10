from django import forms


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=20, label="", required=False, initial=1)


class CouponForm(forms.Form):
    code = forms.CharField(
        label="discount code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
