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
    
    for food in today_orders:
        if food.composition in composition_list:
            composition_list[food.composition] = composition_list.get(food.composition,0) + 1
        else:
            composition_list[food.composition] = 1
    
    send_mail(
        f'Lista obiadów {today.date()}',
        composition_list,
        None,
        ['damian.jadacki@linetech.pl'],
        fail_silently=False,
    )