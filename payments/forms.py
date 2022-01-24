from django import forms

from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit


class TopUpForm(forms.Form):
    top_up_amount = forms.IntegerField(label='Enter the amount', min_value=15, max_value=10000, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Top up your account',
            ),
            AppendedText('top_up_amount', 'pln'),
            ButtonHolder(
                Submit('submit', 'Checkout', css_class='mt-2')
            )
        )