from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms


class TopUpForm(forms.Form):
    amount = forms.IntegerField(label='Enter the amount', min_value=15, max_value=10000, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Top up your account',
            ),
            AppendedText('amount', 'pln'),
            ButtonHolder(
                Submit('submit', 'Checkout', css_class='mt-2')
            )
        )
