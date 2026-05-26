from django import forms

from apps.promotions.models import Coupon


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "Coupon code"}),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon or not coupon.is_valid():
            raise forms.ValidationError("Invalid or expired coupon code.")
        self.coupon = coupon
        return code


class CheckoutForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Coupon code"}),
    )
    use_referral_credit = forms.BooleanField(required=False, initial=False)
