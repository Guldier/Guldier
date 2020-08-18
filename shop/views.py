from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dish


def home (request):
    context = {
        'dish': Dish.objects.all(),
        'title': 'Home',
        'type': 'all'
    }
    return render(request, 'shop/home.html',context)


def about (request):
    return render(request, 'shop/about.html', {'title': 'About'})


def select_type(request, type):
    if type == "all":
       return redirect('shop-home')
    else:
        context ={
            'dish':Dish.objects.filter(dish_type = type),
            'title': 'Home',
            'type': type
        } 
        return render(request, 'shop/home.html',context)
    