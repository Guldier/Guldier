from django import forms

from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import InlineRadios
from .models import ToUpValueAndDiscount


class TopUpForm(forms.Form):

    PAYMENTS_VALUE = [(top_up, top_up) for top_up in ToUpValueAndDiscount.objects.all()]

    # PAYMENTS_VALUE = [
    #     ('15', 15),
    #     ('25', 25),
    #     ('50', 50),
    #     ('100', 100),
    #     ('200', 200),
    #     ('500', 500),
    # ]

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
            )
        )




