from django import forms
from apps.orders.models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model  = Address
        fields = [
            'label', 'full_name', 'phone',
            'line1', 'line2',
            'country', 'state', 'city', 'postcode',
            'is_default',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent styling to all fields
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'ac-addr-checkbox-input'})
            else:
                field.widget.attrs.update({
                    'class': 'ac-addr-input',
                })

        # Placeholders
        self.fields['label'].widget.attrs['placeholder']    = 'e.g. Home, Office'
        self.fields['full_name'].widget.attrs['placeholder'] = 'Full name'
        self.fields['phone'].widget.attrs['placeholder']    = '+44 7700 000000'
        self.fields['line1'].widget.attrs['placeholder']    = 'Street address'
        self.fields['line2'].widget.attrs['placeholder']    = 'Apartment, suite, etc. (optional)'
        self.fields['city'].widget.attrs['placeholder']     = 'City'
        self.fields['state'].widget.attrs['placeholder']    = 'State or region'
        self.fields['postcode'].widget.attrs['placeholder'] = 'Postcode'
        self.fields['country'].widget.attrs['placeholder']  = 'Country'

        # Required overrides
        self.fields['label'].required  = False
        self.fields['line2'].required  = False
        self.fields['phone'].required  = True
        self.fields['state'].required  = True
        self.fields['postcode'].required = True