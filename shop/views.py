from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Dish, 
    AddOn
)

title = 'Home'

def home (request):
    context = {
        'dish': Dish.objects.all(),
        'title': title,
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
            'title': title,
            'type': type
        } 
        return render(request, 'shop/home.html',context)

def open_dish(request, dish):
    context = {
        'dish': Dish.objects.filter(id=dish),
        'titele': title,
        'addon': AddOn.objects.filter(addon_type='first')
    }
    return render(request, 'shop/home.html', context)
    
def add_to_cart(request, dish, addon):
    #addtoTempCart
    #selectFromTempCart
    #render
    return