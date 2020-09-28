from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MoneyMovement,Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required = True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class MoneyMove(ModelForm):
    money = forms.ModelChoiseField(queryset=Profile.objects.all())
    class Meta:
        model = MoneyMovement
        fields = ['Profile', 'moneyMove']