from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from payments import forms as pay_forms
from payments import models as pay_models
from payments import schemas as pay_schemas
from urllib.parse import urljoin
from users.models import Profile
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class ProductLandingPageView(View):

    def get(self, request, *args, **kwargs):
        form = pay_forms.TopUpForm()
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'form': form,
        }
        return render(request, template_name='top_up.html', context=context)


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        form = pay_forms.TopUpForm(request.POST)
        if form.is_valid():
            topup_value = form.cleaned_data['top_up_amount']
        else:
            return redirect('payments:top_up')
        intent_value = int(topup_value) * 100
        schema = 'http://'
        host = request.META['HTTP_HOST']
        hostname = host.split(':')[0]
        port = host.split(':')[1]
        success_url = urljoin(schema + hostname + ':' + port, '/profile')
        cancel_url = urljoin(schema + hostname + ':' + port, '/payments/cancel')
        user = request.user
        currency = 'pln'
        name = 'wplata'
        quantity = 1
        product_data = pay_schemas.ProductData(name=name)
        price_data = pay_schemas.PriceData(currency=currency, unit_amount=intent_value, product_data=product_data)
        line_items = pay_schemas.LineItems(price_data=price_data, quantity=quantity)
        metadata = pay_schemas.Metadata(user_profile_id=user.profile.id)
        line_items_json = pay_schemas.LineItemsSchema().dump(line_items)
        metadata_json = pay_schemas.MetadataSchema().dump(metadata)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                line_items_json,
            ],
            metadata=metadata_json,
            mode='payment',
            payment_intent_data={'metadata': metadata_json},
            success_url=success_url,
            cancel_url=cancel_url,
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

        if event.type == 'payment_intent.created':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_amount_data(event_body, topup)
        elif event.type == 'payment_intent.succeeded':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            increase_balance(event_body)
        elif event.type == 'payment_intent.payment_failed':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'payment_intent.processing':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'payment_intent.cancelled':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'charge.failed':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'charge.pending':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'charge.refunded':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        # todo --> design refund flow
        elif event.type == 'charge.succeeded':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'checkout.session.expired':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'checkout.session.completed':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
        elif event.type == 'customer.created':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'customer.updated':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)

        return HttpResponse(status=200)


def object_check(event):
    event_body = event.data.object
    if event.type in ['customer.created', 'customer.updated']:
        customer_id = event_body.id
    else:
        customer_id = event_body.customer
    object_type = event_body.object
    try:
        topup = pay_models.TopUp.object.get(customer_id=customer_id)
    except pay_models.TopUp.DoesNotExist:
        topup = pay_models.TopUp.object.create(customer_id=customer_id)
    return event_body, topup, object_type

def save_body(event_body, topup, object_type):
    if object_type == 'checkout.session':
        topup.checkout_session_body = event_body
    elif object_type == 'payment_intent':
        topup.payment_intent_body = event_body
    elif object_type == 'charge':
        topup.charge_body = event_body
    elif object_type == 'customer':
        topup.customer_body = event_body
    topup.save()

def save_status(event_body, topup, object_type):
    if object_type == 'checkout.session':
        topup.checkout_session_status = event_body.status
    elif object_type == 'payment_intent':
        topup.payment_intent_status = event_body.status
    elif object_type == 'charge':
        topup.charge_status = event_body.status
    topup.save()

def save_id(event_body, topup, object_type):
    if object_type == 'checkout.session':
        topup.checkout_session_id = event_body.id
    elif object_type == 'payment_intent':
        topup.payment_intent_id = event_body.id
    elif object_type == 'charge':
        topup.charge_id = event_body.id
    elif object_type == 'customer':
        topup.customer_id = event_body.id
    topup.save()

def save_email(event_body, topup):
    customer_email = event_body.email
    topup.customer_email = customer_email
    topup.save()

def save_amount_data(event_body, topup):
    amount = event_body.amount
    currency = event_body.currency
    topup.amount = amount
    topup.currency = currency
    topup.save()

def is_live_mode(event_body, topup):
    live_mode = event_body.livemode
    live_mode = event_body.currency
    topup.amount = amount
    topup.currency = currency
    topup.save()

def increase_balance(event_body):
    amount_received = int(event_body.amount / 100)
    user_profile_id = event_body.metadata.user_profile_id
    profile = Profile.objects.get(pk=user_profile_id)
    profile.money += amount_received
    profile.save()
