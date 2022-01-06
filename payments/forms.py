from django import forms


class TopUpForm(forms.Form):
    top_up_amount = forms.IntegerField(label='Enter topup amount', min_value=2, max_value=10000, required=True, error_messages={'required': 'Please enter topup amount'})
