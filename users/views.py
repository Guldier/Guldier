from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, MoneyMove
from .models import Profile
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime,time

startTime = time(5,00)
endTime = time(9,00)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome! You are now able to login {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    context = {
        'time': datetime.now(),
        'hoursStart': startTime,
        'hoursEnd': endTime,
        'form': form
    }
    return render(request, 'users/register.html', context)


@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = Profile(user=request.user)
        profile.save()

    context  = {
        'users_log': Profile.objects.filter(user = request.user).exists(),
        'profile_view': True,
        'money': profile.money,
        'time': datetime.now(),
        'hoursStart': startTime,
        'hoursEnd': endTime,
    }

    return render(request, 'users/profile.html', context)

@login_required
def feed_account(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form = MoneyMove(request.POST)
            if form.is_valid():
                form.save()   
                profile = form.cleaned_data.get('profile')
                money = form.cleaned_data.get('moneyMove')
                profile_update = Profile.objects.get(user=profile.user)
                profile_update.money += money
                profile_update.save()
                messages.success(request, f'Added {money} zł to {profile.user}')
        else:
            form = MoneyMove()    
        context  = {
            'summary': True,
            'money': Profile.objects.get(user=request.user).money,
            'form': form
        }
        return render(request, 'users/feedme.html',context)
    else:
        return redirect('shop-home')
        