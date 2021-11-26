from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.views.generic import TemplateView

import stripe
from .models import Price


stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductLandingPageView(TemplateView):
    template_name = 'top_up.html'

    def get_context_data(self, **kwargs):

        price_pk = self.kwargs['pk']
        
        price = Price.objects.get(pk=price_pk)
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,

            "product": 'Doładowanie punktów',
            "price": price,
        })
        return context


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):

        YOUR_DOMAIN = 'http://127.0.0.1:8000'

        price_pk = self.kwargs['pk']
        price = Price.objects.get(pk=price_pk)

        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    # Provide the exact Price ID (e.g. pr_1234) of the product you want to sell
                    'price': price.stripe_id,
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