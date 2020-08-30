from django.urls import path
from . import views
from .views import (
    select_type,
    open_dish,
    add_to_cart,
    delete_from_cart,
    order_summary,
    add_to_cart_summary,
    remove_from_cart_summary,
    delete_from_cart_summary,
    buy,
    show_history
)

urlpatterns = [
    path('', views.home, name='shop-home'),
    path('about/', views.about, name='shop-about'),
    path('select_type/<str:type>/', select_type, name='shop-select'),
    path('open_dish/<int:dish>/', open_dish, name='shop-open-dish'),
    path('add_cart/<int:dish>/', add_to_cart, name='shop-add-cart'),
    path('delete_cart/<int:composition>/', delete_from_cart, name='shop-delete-from-cart'),
    path('order_summary/', order_summary, name='shop-order-summary'),
    path('add_cart/summary/<int:composition>', add_to_cart_summary, name='shop-add-summary'),
    path('remove_cart/summary/<int:composition>', remove_from_cart_summary, name='shop-remove-summary'),
    path('delete_cart_summary/<int:composition>/', delete_from_cart_summary, name='shop-delete-from-cart-summary'),
    path('buy/', buy, name='shop-buy'),
    path('history/',show_history, name='shop-history')
]