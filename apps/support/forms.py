from django import forms
from .models import SupportEnquiry


class SupportEnquiryForm(forms.ModelForm):
    class Meta:
        model = SupportEnquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Your Full Name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'you@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 800 000 0000',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Subject (e.g. Order Delivery Inquiry or Merchant Support)',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Explain your question, order issue, or feedback in detail...',
                'rows': 5,
                'required': True,
            }),
        }
