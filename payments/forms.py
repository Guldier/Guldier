from re import template
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field
from crispy_forms.bootstrap import InlineRadios

from .models import Address


class AmountAddressForm(forms.Form):

    PAYMENTS_VALUE = [
        ('15', 15),
        ('25', 25),
        ('50', 50),
        ('100', 100),
        ('200', 200),
        ('500', 500),
    ]

    top_up_amount = forms.ChoiceField(required=True, widget=forms.RadioSelect,
                                      choices=PAYMENTS_VALUE)
    
    ADDRESS_CHOICE = [
        ('last', ' Use the last used address:'),
        ('new', ' Use a new address'),
    ]

    address_choice = forms.ChoiceField(widget=forms.RadioSelect, required=False,
                                      choices=ADDRESS_CHOICE)

    name = forms.CharField(max_length=128, required=False)
    surname = forms.CharField(max_length=128, required=False)
    street_and_number = forms.CharField(max_length=256, required=False)
    city = forms.CharField(max_length=128, required=False)
    country = forms.CharField(max_length=128, required=False)
    postal_code = forms.CharField(max_length=6, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout( 
            Fieldset(
                'Choose the amount (pln):'),
            InlineRadios('top_up_amount'),
            Fieldset(
                'Provide data for invoice:'),
            InlineRadios('address_choice', template='crispy/address_choice.html'),
            Fieldset(
                '',
                Field('name', css_class='form-control mb-2'),
                Field('surname', css_class='form-control mb-2'),
                Field('street_and_number', css_class='form-control mb-2'),
                Field('city', css_class='form-control mb-2'),
                Field('country', css_class='form-control mb-2'),
                Field('postal_code', css_class='form-control mb-2', id='postal-code'),
                id='new-address'),
            ButtonHolder(
                Submit('submit', 'Checkout', css_class='form-control mt-2'),
            ),
        )
    
    # class Meta:
    #     model = Address
    #     fields = ['name', 'surname', 'street_and_number', 'city', 'country', 'postal_code']