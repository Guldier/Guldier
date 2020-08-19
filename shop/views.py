from django.shortcuts import render
from .models import Dish


def home (request):
    context = {
        'dish': Dish.objects.all(),
        'title': 'Home'
    }
    return render(request, 'shop/home.html',context)

def about (request):
    return render(request, 'shop/about.html', {'title': 'About'})