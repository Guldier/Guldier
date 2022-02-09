from django import views
from django.urls import path
from payments import views as pay_views

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', pay_views.CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('success/', pay_views.SuccessView.as_view(), name='success'),
    path('cancel/', pay_views.CancelView.as_view(), name='cancel'),
    path('top-up/', pay_views.ProductLandingPageView.as_view(), name='top_up'),
    path('webhooks/stripe/', pay_views.WebhookView.as_view(), name='stripe-webhook'),
    path('history/', pay_views.PaymentHistoryView.as_view(), name='payment_history'),
    path('invoice/<int:topup_pk>', pay_views.GetInvoiceView.as_view(), name='invoice_pdf'),
]