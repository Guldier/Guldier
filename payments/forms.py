from django import forms
import datetime

from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
from .models import Promotion

from .utils import calculate_discounts


class TopUpForm(forms.Form):
    promotions = Promotion.objects.all()
    promotion_id = None

    if len(promotions) > 0:
        PAYMENTS_VALUE, promotion_id = calculate_discounts(promotions)

    else:
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
