from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from rest_framework.utils import json
from users.models import Profile
import stripe
from payments import forms, schemas as pay_schemas
from payments import forms as pay_forms

stripe.api_key = settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class ProductLandingPageView(View):

    def get(self, request, *args, **kwargs):
        form = pay_forms.TopUpForm()
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "product": 'Doładowanie punktów',
            'form': form,
        }
        return render(request, template_name = 'top_up.html', context=context)


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        form = pay_forms.TopUpForm(request.POST)
        if form.is_valid():
            topup_value = form.cleaned_data['top_up_amount']
        intent_value = int(topup_value) * 100
        YOUR_DOMAIN = 'http://127.0.0.1:8000'
        user = request.user

        currency = 'pln'
        name = 'wplata'
        quantity = 1
        
        product_data = pay_schemas.ProductData(name=name)
        price_data = pay_schemas.PriceData(currency=currency, unit_amount=intent_value, product_data=product_data)
        line_items = pay_schemas.LineItems(price_data=price_data, quantity=quantity)
        metadata = pay_schemas.Metadata(user_profile_id=user.profile.id)

        line_items_json = pay_schemas.LineItemsSchema().dump(line_items)
        print(line_items_json)
        metadata_json = pay_schemas.MetadataSchema().dump(metadata)
        print(metadata_json)


        checkout_session = stripe.checkout.Session.create(
            line_items=[
                line_items_json,
            ],
            metadata=metadata_json,
            mode='payment',
            success_url=YOUR_DOMAIN + '/profile',
            cancel_url=YOUR_DOMAIN + '/payments/cancel',
        )

        return redirect(checkout_session.url, code=303, context={'message': 'Your account has been topped up.'})


class SuccessView(TemplateView):
    template_name = 'success.html'


class CancelView(TemplateView):
    template_name = 'cancel.html'


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):

    def post(self, request, *args, **kwargs):
        
        payload = request.body
        # header in the response that is coming from Stripe
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        print(f'Sig_header: {sig_header}, stripe api key: {stripe.api_key}, endpoint secret: {endpoint_secret}')
        event = None

        # try:
        #     event = stripe.Event.construct_from(
        #         json.loads(payload), sig_header, stripe.api_key
        #     )
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event.type == 'checkout.session.completed':
            completed_checkout_session = event.data.object
            amount_received = int(completed_checkout_session.amount_total / 100)
            user_profile_id = completed_checkout_session.metadata.user_profile_id
            profile = Profile.objects.get(pk=user_profile_id)
            profile.money += amount_received
            profile.save()

            # send_mail(
            #     subject='Your account has been topped up',
            #     message='Thanks for your purchase',
            #     recipient_list=[customer_email],
            #     from_email='some_email@test.com',
            # )
        # # Passed signature verification
        return HttpResponse(status=200)
