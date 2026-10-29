from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from .models import Address

User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Last Name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 800 000 0000',
            }),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['recipient_name', 'phone', 'street_address', 'apartment_suite', 'city', 'state', 'postal_code', 'is_default']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Recipient Full Name',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 800 000 0000',
                'required': True,
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Street Address & House Number',
                'required': True,
            }),
            'apartment_suite': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Apartment, Suite, Unit (Optional)',
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'City / District',
                'required': True,
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'State / Province (e.g. FCT Abuja or Lagos)',
                'required': True,
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Postal Code',
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]',
            }),
        }


class ChangePasswordForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-[#E53935]',
            })
