from django.urls import path
from . import views
from .views import (
    select_type
)

urlpatterns = [
    path('', views.home, name='shop-home'),
    path('about/', views.about, name='shop-about'),
    path('select_type/<str:type>/', select_type, name='shop-select'),
]