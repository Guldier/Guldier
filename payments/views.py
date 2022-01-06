from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from users.models import Profile
from urllib.parse import urljoin

import stripe
from rest_framework.utils import json

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductLandingPageView(TemplateView):
    template_name = 'top_up.html'

    def get_context_data(self, **kwargs):
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        })
        return context


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        topup_value = request.POST.get('topup')
        intent_value = int(topup_value) * 100
        schema = 'http://'
        host = request.META['HTTP_HOST']
        hostname = host.split(':')[0]
        port = host.split(':')[1]
        success_url = urljoin(schema + hostname + ':' + port, '/profile')
        cancel_url = urljoin(schema + hostname + ':' + port, '/payments/cancel')
        user = request.user
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
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
            metadata={
                "user_profile_id": user.profile.id
            },
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return redirect(checkout_session.url, code=303, context={'message': 'Your account has been topped up.'})


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    # header in the response that is coming from Stripe
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), sig_header, stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        completed_checkout_session = event.data.object
        print(completed_checkout_session)
        amount_received = int(completed_checkout_session.amount_total / 100)
        user_profile_id = completed_checkout_session.metadata.user_profile_id
        profile = Profile.objects.get(pk=user_profile_id)
        profile.money += amount_received
        profile.save()
    return HttpResponse(status=200)
