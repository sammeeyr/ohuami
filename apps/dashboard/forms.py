from decimal import Decimal
from django import forms
from apps.catalog.models import Product, Store, Category, Brand
from apps.orders.models import Order, OrderItem
from apps.promotions.models import Coupon
from .models import StoreAgent, DispatchCarrier, DispatchShipment, StoreCustomer


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MerchantProductForm(forms.ModelForm):
    primary_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'block w-full text-xs text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-[#111111] file:text-white hover:file:bg-black cursor-pointer',
            'id': 'id_primary_image',
        })
    )
    additional_images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'accept': 'image/*',
            'multiple': True,
            'class': 'block w-full text-xs text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-gray-100 file:text-gray-800 hover:file:bg-gray-200 cursor-pointer',
            'id': 'id_additional_images',
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'base_price', 'comparison_price', 
            'sku', 'stock_quantity', 'description', 'badge_text', 
            'is_flash_sale', 'is_featured', 'is_trending', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Product Title (e.g. Silk Evening Dress or Wireless Earbuds)',
                'required': True,
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'brand': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
            }),
            'base_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '28000.00',
                'step': '0.01',
                'required': True,
            }),
            'comparison_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '35000.00',
                'step': '0.01',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'SF-DRS-001',
                'required': True,
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '50',
                'required': True,
            }),
            'badge_text': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'e.g. -20% or Hot or Bestseller',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Detailed product description, fabric, dimensions, specifications...',
                'rows': 4,
                'required': True,
            }),
            'is_flash_sale': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#10B981] rounded'}),
        }


class MerchantOrderManualCreateForm(forms.Form):
    """Allows merchants to register manual, in-store, or WhatsApp orders directly."""
    customer_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'placeholder': 'Customer Full Name',
        'required': True,
    }))
    customer_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'placeholder': 'customer@example.com',
        'required': True,
    }))
    customer_phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'placeholder': '+234 801 234 5678',
        'required': True,
    }))
    shipping_street_address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'placeholder': '128, Ganiyu Street, GRA',
        'required': True,
    }))
    shipping_city = forms.CharField(max_length=100, initial='Abuja', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'required': True,
    }))
    shipping_state = forms.CharField(max_length=100, initial='FCT', widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'required': True,
    }))
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
            'required': True,
        })
    )
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        'required': True,
    }))
    shipping_fee = forms.DecimalField(max_digits=10, decimal_places=2, initial=Decimal('2000.00'), widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
    }))
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash on Delivery / Walk-in'),
            ('bank_transfer', 'Direct Bank Transfer'),
            ('pos_terminal', 'POS Terminal Sync'),
            ('paystack', 'Paystack Online'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        })
    )
    payment_status = forms.ChoiceField(
        choices=Order.PaymentStatus.choices,
        initial=Order.PaymentStatus.PAID,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        })
    )
    fulfillment_status = forms.ChoiceField(
        choices=Order.FulfillmentStatus.choices,
        initial=Order.FulfillmentStatus.PROCESSING,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
        })
    )

    def __init__(self, *args, **kwargs):
        store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        if store:
            self.fields['product'].queryset = Product.objects.filter(store=store, is_active=True)
        else:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)


class StoreAgentForm(forms.ModelForm):
    class Meta:
        model = StoreAgent
        fields = [
            'name', 'email', 'phone', 'role',
            'can_manage_products', 'can_manage_orders', 
            'can_manage_dispatch', 'can_manage_customers', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Agent Full Name (e.g. Amaka Obi)',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'amaka@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 802 345 6789',
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'can_manage_products': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'can_manage_orders': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'can_manage_dispatch': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'can_manage_customers': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#E53935] rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#10B981] rounded'}),
        }


class DispatchCarrierForm(forms.ModelForm):
    class Meta:
        model = DispatchCarrier
        fields = [
            'name', 'carrier_type', 'contact_person', 'phone',
            'email', 'vehicle_type', 'vehicle_number', 'service_areas', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Carrier or Rider Name (e.g. GIG Logistics or Tunde In-House)',
                'required': True,
            }),
            'carrier_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Contact Person / Fleet Lead',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 803 456 7890',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'dispatch@logistics.ng',
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
            }),
            'vehicle_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Plate number (e.g. KJA-821-XX)',
            }),
            'service_areas': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Lagos Mainland, Lekki, Victoria Island, Ikeja',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#10B981] rounded'}),
        }


class DispatchShipmentForm(forms.ModelForm):
    class Meta:
        model = DispatchShipment
        fields = [
            'carrier', 'delivery_address', 'recipient_name', 'recipient_phone',
            'dispatch_notes', 'estimated_delivery', 'status'
        ]
        widgets = {
            'carrier': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
            }),
            'delivery_address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'recipient_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'dispatch_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Gate instructions, landmark, package handling care...',
                'rows': 3,
            }),
            'estimated_delivery': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'type': 'date',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-semibold focus:outline-none focus:border-[#E53935]',
            }),
        }

    def __init__(self, *args, **kwargs):
        store = kwargs.pop('store', None)
        super().__init__(*args, **kwargs)
        if store:
            self.fields['carrier'].queryset = DispatchCarrier.objects.filter(store=store, is_active=True)


class StoreCustomerForm(forms.ModelForm):
    class Meta:
        model = StoreCustomer
        fields = ['name', 'email', 'phone', 'customer_tag', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Customer Full Name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'customer@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '+234 801 234 5678',
            }),
            'customer_tag': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-semibold focus:outline-none focus:border-[#E53935]',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Internal notes (e.g. VIP client, preferred sizing, payment terms)...',
                'rows': 3,
            }),
        }


class StoreCorsApiForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['cors_allowed_origins', 'api_key_enabled']
        widgets = {
            'cors_allowed_origins': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'http://localhost:3000, https://yourstorefront.ng, https://m.yourstore.com',
                'rows': 3,
            }),
            'api_key_enabled': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-[#10B981] rounded'}),
        }


class MerchantStoreSettingsForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name', 'tagline', 'description', 'custom_domain',
            'bank_name', 'bank_account_number', 'bank_account_name', 'payout_schedule',
            'cors_allowed_origins'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'required': True,
            }),
            'tagline': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'e.g. Style that speaks you. Trendy. Classy. Affordable.',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'rows': 3,
            }),
            'custom_domain': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'yourbrand.com (requires Pro or Enterprise plan)',
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Access Bank, GTBank, Zenith Bank, etc.',
            }),
            'bank_account_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '10-digit NUBAN account number',
            }),
            'bank_account_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'Registered Corporate or Personal Account Name',
            }),
            'payout_schedule': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
            }),
            'cors_allowed_origins': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'http://localhost:3000, https://sunshinefashion.ng',
                'rows': 2,
            }),
        }


class MerchantCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_type', 'discount_value', 'min_order_value', 'usage_limit']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm uppercase font-bold focus:outline-none focus:border-[#E53935]',
                'placeholder': 'SUMMER20 or FLASH10',
                'required': True,
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': 'e.g. 10% off your entire order',
            }),
            'discount_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-semibold focus:outline-none focus:border-[#E53935]',
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '10 (for 10%) or 2000 (for ₦2,000)',
                'step': '0.01',
                'required': True,
            }),
            'min_order_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-[#E53935]',
                'placeholder': '100',
            }),
        }
