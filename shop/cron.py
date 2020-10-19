from datetime import datetime
from django.core.mail import send_mail
from .models import (
    Dish, 
    AddOn,
    Composition,
    Cart,
    Orders,
    WeekDish
)

def create_list():
    today = datetime.today()
    today_orders=Orders.objects.filter(order_date__date=today.date())
    composition_list = {}
    money = 0
    
    for food in today_orders:
        if food.user.is_stuff:
            pass
        else:
            if food.composition in composition_list:
                composition_list[food.composition] = composition_list.get(food.composition,0) + food.quantity
            else:
                composition_list[food.composition] = food.quantity
    
    message = 'PODUMOWANIE WSZYSTKICH DAŃ\n'

    for key in composition_list:
        message += f'{key} x {composition_list[key]}\n'

    message += '\nOsoby zamawiające\n'

    for orders in today_orders:
        message += f'{orders.user} - {orders.composition} - {orders.quantity}szt.\n'
	money += orders.compositions.dish.price*orders.quantity

    message += f'Łącznie do zapłaty: {money}zł\n'
    message += '\nPozdrawiamy\nLinetech'
    
    send_mail(
        f'Lista obiadów {today.date()}',
        message,
        None,
        ['damian.jadacki@linetech.pl'],
        fail_silently=False,
    )

def create_list_rep():
    today = datetime.today()
    today_orders=Orders.objects.filter(order_date__date=today.date())
    composition_list = {}

    for food in today_orders:
        if food.user.is_stuff:
            if food.composition in composition_list:
                composition_list[food.composition] = composition_list.get(food.composition,0) + food.quantity
            else:
                composition_list[food.composition] = food.quantity
    
    message = 'Pani Zosiu,\n'
    message += 'Zamówienie:\n'

    for key in composition_list:
        message += f'{key} x {composition_list[key]}\n'

    message += '\nOsoby zamawiające\n'

    for orders in today_orders:
        message += f'{orders.user} - {orders.composition} - {orders.quantity}szt.\n'

    message += 'Jak zawsze proszę o dopisanie do FV z obiadami dla rep\n Dziękuje\nOla Cynk'

    send_mail(
        f'Lista obiadów rep {today.date()}',
        message,
        None,
        ['damian.jadacki@linetech.pl'],
        fail_silently=False,
    )
