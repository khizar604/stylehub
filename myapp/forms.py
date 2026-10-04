from django import forms
from .models import BrandSubmission

class BrandSubmissionForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to the terms and conditions',
        error_messages={'required': 'You must agree to the terms to proceed'}
    )

    class Meta:
        model = BrandSubmission
        fields = [
            'first_name', 'last_name', 'brand_name', 'category',
            'deal_percentage', 'product_image', 'whatsapp_number',
            'email'
        ]


from django import forms

class EmailForm(forms.Form):
    email = forms.EmailField()

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
