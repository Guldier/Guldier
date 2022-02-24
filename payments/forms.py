from django import forms
import datetime

from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios

from payments import models as pay_models

from .utils import calculate_discounts


class TopUpForm(forms.Form):
    PAYMENTS_VALUE = [(price.amount, str(price.amount) + ' za ' + f'{price.get_discounted_price:.2f}')
                      if price.promotion.active_dates.date_within_range
                      and price.promotion.active else (price.amount, price.amount)
                      for price in pay_models.Price.objects.all().order_by('amount')]

    top_up_amount = forms.ChoiceField(required=True, widget=forms.RadioSelect,
                                      choices=PAYMENTS_VALUE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Top up your account PLN'),
            InlineRadios("top_up_amount", css_class='radio_btn'),
            ButtonHolder(
                Submit('submit', 'Checkout', css_class='mt-2'),
            ),
        )
