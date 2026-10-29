from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['customer_name', 'rating', 'title', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Your Name or Nickname',
                'required': True,
            }),
            'rating': forms.Select(choices=[(5, '★★★★★ (5 Stars - Excellent)'), (4, '★★★★☆ (4 Stars - Very Good)'), (3, '★★★☆☆ (3 Stars - Average)'), (2, '★★☆☆☆ (2 Stars - Poor)'), (1, '★☆☆☆☆ (1 Star - Terrible)')], attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935] font-semibold',
                'required': True,
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Headline for your review (e.g. Great quality and fits perfectly!)',
                'required': True,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Write your full review here. How was the material, packaging, delivery, and overall experience?',
                'rows': 4,
                'required': True,
            }),
        }
