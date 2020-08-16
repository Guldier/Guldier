from django.shortcuts import render

menu = [
    {'name': 'Danie dnia',
    'ingredient': 'Kurczak',
    'price': '16'
    },
    {'name': 'Zupa dnia',
    'ingredient': 'Pomidorowa',
    'price': '5'
    }    
]

def home (request):
    context = {
        'dish': menu,
        'title': 'Home'
    }
    return render(request, 'shop/home.html',context)


def about (request):
    return render(request, 'shop/about.html', {'title': 'About'})