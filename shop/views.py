from datetime import datetime,time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,TemplateView,CreateView
from django.contrib.auth.models import User
from django.db.models import Sum
import calendar
from .models import (
    Dish, 
    AddOn,
    Composition,
    Cart,
    Orders,
    WeekDish
)
from users.models import (
    Profile
)


startTime = time(5,00)
endTime = time(9,00)

def check_time():
    now = datetime.now()
    if now.time() > startTime and now.time() < endTime:
        return True
    else:
        return False

def countTotalPrice(user):
    items_in_cart = Cart.objects.filter(user=user)
    total_price = 0
    for item in items_in_cart:
        composition_price = item.composition.dish.price + item.composition.addon.price
        total_price += composition_price * item.quantity
        
    value_to_return ={
        'total_price': total_price,
        'items_in_cart': items_in_cart
    }
    return value_to_return
    
def selectMenu(type):
    today = datetime.today()
    if type == 'all':
        allDish = Dish.objects.all()
        if today.weekday()<5:
            for dish in allDish:
                if dish.dish_type == 'special':
                    if dish.name == 'Zestaw dnia':
                        dish_day = WeekDish.objects.get(name='Danie dnia', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    elif dish.name == 'Zestaw dnia FIT':
                        dish_day = WeekDish.objects.get(name='Danie dnia FIT', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia FIT', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    try:
                        weekdish = WeekDish.objects.get(name=dish.name, day=today.weekday())               
                        dish.ingredient = weekdish.ingredient
                    except:
                        pass
            returndish = allDish
        else:
            for dish in allDish:
                if dish.dish_type == 'special':
                    dish.ingredient = 'Weekend'   
            returndish = allDish             
    elif type == 'special':
        allDish = Dish.objects.filter(dish_type = type)
        if today.weekday()<5:
            for dish in allDish:
                if dish.dish_type == 'special':
                    if dish.name == 'Zestaw dnia':
                        dish_day = WeekDish.objects.get(name='Danie dnia', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    elif dish.name == 'Zestaw dnia FIT':
                        dish_day = WeekDish.objects.get(name='Danie dnia FIT', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia FIT', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    try:
                        weekdish = WeekDish.objects.get(name=dish.name, day=today.weekday())               
                        dish.ingredient = weekdish.ingredient
                    except:
                        pass
            returndish = allDish
        else:
            for dish in allDish:
                if dish.dish_type == 'special':
                    dish.ingredient = 'Weekend'   
            returndish = allDish             
    else:
        returndish = Dish.objects.filter(dish_type = type)

    return returndish

def home (request):    
    context = {
        'dish': selectMenu('all'),
        'type': 'all',
        'hoursStart': startTime,
        'hoursEnd': endTime,
        'time': datetime.now()
    }
    try:
        values = countTotalPrice(request.user)    
        context.update({'cart': values["items_in_cart"], 'sum_price': values["total_price"]}) 
        money = Profile.objects.get(user=request.user).money
        context.update({'money': money})
    except:
        pass    

    return render(request, 'shop/home.html',context)

def about (request):
    context = {
        'summary': True
    }
    return render(request, 'shop/about.html', context)

def select_type(request, type):
    if type == "all":
       return redirect('shop-home')
    else:
        context = {
            'dish':selectMenu(type),
            'type': type
        }

        try:
            values = countTotalPrice(request.user)    
            context.update({'cart': values["items_in_cart"], 'sum_price': values["total_price"]}) 
            money = Profile.objects.get(user=request.user).money
            context.update({'money': money})
        except:
            pass    
        return render(request, 'shop/home.html',context)

def open_dish(request, dish):
    today = datetime.today()
    type = Dish.objects.get(id=dish).dish_type
    dishO = Dish.objects.filter(id=dish)
    
    if type == 'special':       
        if today.weekday()<5:
            for dish in dishO:
                if dish.dish_type == 'special':
                    if dish.name == 'Zestaw dnia':
                        dish_day = WeekDish.objects.get(name='Danie dnia', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    elif dish.name == 'Zestaw dnia FIT':
                        dish_day = WeekDish.objects.get(name='Danie dnia FIT', day=today.weekday())
                        soup_day = WeekDish.objects.get(name='Zupa dnia FIT', day=today.weekday())
                        dish.ingredient = dish_day.ingredient + ' + ' + soup_day.ingredient
                    try:
                        weekdish = WeekDish.objects.get(name=dish.name, day=today.weekday())               
                        dish.ingredient = weekdish.ingredient
                    except:
                        pass
        else:
            for dish in allDish:
                if dish.dish_type == 'special':
                    dish.ingredient = 'Weekend'           

    context = {
        'dish': dishO,
        'addon': AddOn.objects.filter(addon_type=type),
        'open': True
    }
    try:
        values = countTotalPrice(request.user)    
        context.update({'cart': values["items_in_cart"], 'sum_price': values["total_price"]}) 
        money = Profile.objects.get(user=request.user).money
        context.update({'money': money})
    except:
        pass    

    return render(request, 'shop/home.html', context)

@login_required 
def add_to_cart(request, dish):
    if check_time():
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
        values = countTotalPrice(request.user)     
        #pobranie nowej nowej kombinacji
        try:
            composition = Composition.objects.get(dish=dishDB, addon=addonDB)
        except Composition.DoesNotExist:
            composition = Composition(dish=dishDB, addon=addonDB)
            composition.save()

        if profil.money < (values['total_price'] + composition.dish.price + composition.addon.price):
            messages.warning(request,'Not enough money')
        else:
            try:
                cart_object = Cart.objects.get(user=user, composition=composition)
                cart_object.quantity += 1
            except:
                cart_object = Cart(user=user, composition=composition)
            cart_object.save()
        
        return redirect('shop-home')
    else:
        return redirect('shop-home')

@login_required
def delete_from_cart(request, composition):
    if check_time():
        item = Cart.objects.get(id=composition)
        item.delete()
    
        return redirect('shop-home')
    else:
        return redirect('shop-home')

@login_required
def order_summary(request):
    if check_time():
        values = countTotalPrice(request.user) 
        context ={
            'orders': values["items_in_cart"],
            'total_price': values["total_price"],
            'summary': True,
            'money': Profile.objects.get(user=request.user).money
        }

        return render(request, 'shop/summary.html', context)
    else:
        return redirect('shop-home')

@login_required 
def add_to_cart_summary(request, composition):
    if check_time():
        user = User.objects.get(id=request.user.id)
        try:
            profil = Profile.objects.get(user=user)
        except:
            messages.warning(request,'Need to feed your account')
            return redirect('shop-order-summary')
        #sprawdzenie zawartosci koszyka
        values = countTotalPrice(request.user)     
        #pobranie nowej nowej kombinacji
        composition = Composition.objects.get(id=composition)

        if profil.money < (values['total_price'] + composition.dish.price + composition.addon.price):
            messages.warning(request,'Not enough money')
        else:
            try:
                cart_object = Cart.objects.get(user=user, composition=composition)
                cart_object.quantity += 1
            except:
                cart_object = Cart(user=user, composition=composition)
            cart_object.save()
        
        return redirect('shop-order-summary')
    else:
        return redirect('shop-home')

@login_required 
def remove_from_cart_summary(request, composition): 
    if check_time():   
        user = User.objects.get(id=request.user.id)
        try:
            profil = Profile.objects.get(user=user)
        except:
            messages.warning(request,'Need to feed your account')
            return redirect('shop-order-summary')
        
        composition = Composition.objects.get(id=composition)
        try:
            cart_object = Cart.objects.get(user=user, composition=composition)
            cart_object.quantity -= 1
        except:
            cart_object = Cart(user=user, composition=composition)
        cart_object.save()
        
        return redirect('shop-order-summary')
    else:
        return redirect('shop-home')

@login_required
def delete_from_cart_summary(request, composition):
    if check_time():
        item = Cart.objects.get(id=composition)
        item.delete()
        
        return redirect('shop-order-summary')
    else:
        return redirect('shop-home')

@login_required
def buy(request):
    if check_time():
        items = Cart.objects.filter(user=request.user)
        values = countTotalPrice(request.user)     
        total_price = values['total_price']
        profile = Profile.objects.get(user=request.user)

        for item in items:
            buy = Orders(user= item.user, composition=item.composition, quantity=item.quantity)
            buy.save()
            item.delete()

        profile.money = profile.money - total_price
        profile.save()

        messages.success(request,'Your order has been placed')

        return redirect('shop-home')
    else:
        return redirect('shop-home')

@login_required
def show_history(request):    
    dates = Orders.objects.filter(user=request.user).dates('order_date','day')
    orders = Orders.objects.filter(user=request.user)
    history = []
    for d in reversed(dates): 
        items = []
        total = 0
        for o in orders:          
            if o.order_date.date() == d:
                items.append(f'{o.composition} x {o.quantity} - {o.composition.dish.price + o.composition.addon.price} zł')
                total += (o.composition.dish.price + o.composition.addon.price) * o.quantity            

        history.append({'date': d, 'items': items, 'price': total})


    context = {
        'summary': True,
        'money': Profile.objects.get(user=request.user).money,
        'history': history
    }
    return render(request,'shop/history.html',context)
