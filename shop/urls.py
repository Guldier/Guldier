from django.urls import path
from . import views
from .views import (
    select_type,
    open_dish,
    add_to_cart,
    delete_from_cart
)

urlpatterns = [
    path('', views.home, name='shop-home'),
    path('about/', views.about, name='shop-about'),
    path('select_type/<str:type>/', select_type, name='shop-select'),
    path('open_dish/<int:dish>/', open_dish, name='shop-open-dish'),
    path('add_cart/<int:dish>/', add_to_cart, name='shop-add-cart'),
    path('delete_cart/<int:composition>/', delete_from_cart, name='shop-delete-from-cart')
]