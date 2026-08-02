from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ProductBooking

class BookingForm(forms.ModelForm):
    class Meta:
        model = ProductBooking
        fields = ['start_date', 'end_date', 'quantity', 'special_requests']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'special_requests': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Any special requests or requirements...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if self.product:
            self.fields['quantity'].widget.attrs.update({
                'class': 'form-control',
                'max': self.product.available_quantity_for_booking,
                'min': 1
            })
            self.fields['quantity'].help_text = f"Max available: {self.product.available_quantity_for_booking}"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        quantity = cleaned_data.get('quantity', 1)
        
        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError("End date must be after start date")
            
            if start_date < timezone.now():
                raise ValidationError("Start date cannot be in the past")
            
            # Check product availability
            if self.product:
                days = (end_date - start_date).days
                if days > self.product.max_booking_days:
                    raise ValidationError(f"Maximum booking days is {self.product.max_booking_days}")
                if days < self.product.min_booking_days:
                    raise ValidationError(f"Minimum booking days is {self.product.min_booking_days}")
                
                available = self.product.get_availability_for_date_range(start_date, end_date)
                if available < quantity:
                    raise ValidationError(f"Only {available} items available for this period")
        
        return cleaned_data