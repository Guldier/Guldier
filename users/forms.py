from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MoneyMovement,Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class MoneyMove(forms.ModelForm):    
    profile = forms.ModelChoiceField(queryset=Profile.objects.all())
    class Meta:
        model = MoneyMovement
        fields = ['profile', 'moneyMove']