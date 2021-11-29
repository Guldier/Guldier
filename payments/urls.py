from django.urls import path
from .views import CreateCheckoutSessionView, SuccessView, CancelView, ProductLandingPageView

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('top-up/', ProductLandingPageView.as_view(), name='top_up'),
]