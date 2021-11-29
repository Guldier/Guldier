from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.models import User

import stripe
from .models import Price, TopUp


stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductLandingPageView(TemplateView):
    template_name = 'top_up.html'

    def get_context_data(self, **kwargs):

        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,

            "product": 'Doładowanie punktów',
            # "price": price,
        })
        return context


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):

        topup_value = request.POST.get('topup')
        intent_value = int(topup_value) * 100

        TopUp.objects.create(amount_intent_payment=topup_value, user=request.user)

        YOUR_DOMAIN = 'http://127.0.0.1:8000'

        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    # Provide the exact Price ID (e.g. pr_1234) of the product you want to sell
                    # 'price': price.stripe_id,
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': intent_value,
                        'product_data': {
                            'name': 'wplata'
                        },
                    },
                    'quantity': 1,
                },
            ],

            mode = 'payment',
            success_url = YOUR_DOMAIN + '/success',
            cancel_url = YOUR_DOMAIN + '/cancel',
        )

        return redirect(checkout_session.url, code=303)


class SuccessView(TemplateView):
    template_name = 'succcess.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


