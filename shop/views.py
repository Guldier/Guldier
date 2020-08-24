from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,TemplateView,CreateView
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import (
    Dish, 
    AddOn,
    Composition,
    Chart
)

from users.models import (
    Profile
)

title = 'Home'

def home (request):
    items_in_cart = Chart.objects.filter(user=request.user.id)
    total_price = 0
    for item in items_in_cart:
        total_price += item.composition.price
        if item.composition.addon.name == 'empty':
            item.composition.addon.name = ' '
        
    context = {
        'dish': Dish.objects.all(),
        'title': title,
        'type': 'all',
        'cart': items_in_cart,
        'sum_price': total_price
    }
    return render(request, 'shop/home.html',context)


def about (request):
    return render(request, 'shop/about.html', {'title': 'About'})


def select_type(request, type):
    if type == "all":
       return redirect('shop-home')
    else:
        items_in_cart = Chart.objects.filter(user=request.user.id)
        total_price = 0
        for item in items_in_cart:
            total_price += item.composition.price
            if item.composition.addon.name == 'empty':
                item.composition.addon.name = ' '
        
        context ={
            'dish':Dish.objects.filter(dish_type = type),
            'title': title,
            'type': type,
            'cart': items_in_cart,
            'sum_price': total_price
        } 
        return render(request, 'shop/home.html',context)

def open_dish(request, dish):
    items_in_cart = Chart.objects.filter(user=request.user.id)
    total_price = 0
    for item in items_in_cart:
        total_price += item.composition.price
        if item.composition.addon.name == 'empty':
            item.composition.addon.name = ' '

    context = {
        'dish': Dish.objects.filter(id=dish),
        'titele': title,
        'addon': AddOn.objects.filter(addon_type='first'),
        'cart': items_in_cart,
        'sum_price': total_price
    }
    return render(request, 'shop/home.html', context)

@login_required 
def add_to_cart(request, dish):
    #pobranie dania
    dishDB = Dish.objects.get(id=dish)
    a=0
    #czy danie ma dodatek
    if dishDB.dish_addon:
        if request.method == 'GET':
            a = request.GET['addon_select']
    else:
        addon_empty = AddOn.objects.get(addon_type='empty')
        a = addon_empty.id

    #podbranie dodatku i klienta
    addonDB = AddOn.objects.get(id=a)
    user = User.objects.get(id=request.user.id)
    try:
        profil = Profile.objects.get(user=user)
    except:
        messages.warning(request,'Need to feed your account')
        return redirect('shop-home')
    #sprawdzenie zawartosci koszyka
    items_in_cart = Chart.objects.filter(user=request.user.id)
    total_price = 0
    for item in items_in_cart:
        total_price += item.composition.price
    
    #pobranie nowej nowej kombinacji
    try:
        composition = Composition.objects.get(dish=dishDB, addon=addonDB)
    except Composition.DoesNotExist:
        price = dishDB.price + addonDB.price
        composition = Composition(dish=dishDB, addon=addonDB, price= price)
        composition.save()


    if profil.money < (total_price + composition.price):
        messages.warning(request,'Not enough money')
    else:
        cart_object = Chart(user=user, composition=composition)
        cart_object.save()
    
    return redirect('shop-home')

def delete_from_cart(request, composition):
    item = Chart.objects.get(id=composition)
    item.delete()
    
    return redirect('shop-home')