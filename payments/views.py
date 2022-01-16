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
        topup_pk = get_new_topup_pk()
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
        metadata = pay_schemas.Metadata(user_profile_id=user.profile.id, topup_pk=topup_pk)
        payment_intent_data = pay_schemas.PaymentIntentData(metadata=metadata)
        line_items_json = pay_schemas.LineItemsSchema().dump(line_items)
        metadata_json = pay_schemas.MetadataSchema().dump(metadata)
        payment_intent_data_json = pay_schemas.PaymentIntentDataSchema().dump(payment_intent_data)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                line_items_json,
            ],
            metadata=metadata_json,
            mode='payment',
            payment_intent_data=payment_intent_data_json,
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
            save_user(event_body, topup)
            is_live_mode(event_body, topup)
            save_email(event_body, topup)
        elif event.type == 'payment_intent.succeeded':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            increase_balance(event_body)
            save_email(event_body, topup)
        elif event.type == 'payment_intent.payment_failed':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'payment_intent.requires_action':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'payment_intent.processing':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'payment_intent.cancelled':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
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
            save_email(event_body, topup)
            # TODO --> design refund flow
        elif event.type == 'charge.succeeded':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'checkout.session.expired':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            save_email(event_body, topup)
        elif event.type == 'checkout.session.completed':
            event_body, topup, object_type = object_check(event)
            save_body(event_body, topup, object_type)
            save_status(event_body, topup, object_type)
            save_id(event_body, topup, object_type)
            breakpoint()

        return HttpResponse(status=200)


def get_new_topup_pk():
    new_topup = pay_models.TopUp.objects.create()
    new_topup_pk = new_topup.pk
    return new_topup_pk

def object_check(event):
    event_body = event.data.object
    object_type = event_body.object
    topup_pk = event_body.metadata.topup_pk
    try:
        topup = pay_models.TopUp.objects.get(payment_id=topup_pk)
    except pay_models.TopUp.DoesNotExist:
        topup = pay_models.TopUp.objects.create() #throw error
    return event_body, topup, object_type

def save_body(event_body, topup, object_type):
    if event_body:
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
    event_body_status = event_body.status
    if event_body_status:
        if object_type == 'checkout.session':
            topup.checkout_session_status = event_body_status
        elif object_type == 'payment_intent':
            topup.payment_intent_status = event_body_status
        elif object_type == 'charge':
            topup.charge_status = event_body_status
        topup.save()

def save_id(event_body, topup, object_type):
    event_body_id = event_body.id
    if event_body_id:
        if object_type == 'checkout.session':
            topup.checkout_session_id = event_body_id
        elif object_type == 'payment_intent':
            topup.payment_intent_id = event_body_id
        elif object_type == 'charge':
            topup.charge_id = event_body_id
        elif object_type == 'customer':
            topup.customer_id = event_body_id
        topup.save()

def save_email(event_body, topup):
    customer_id = event_body.customer
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.email
        topup.customer_email = email
        topup.save()

def save_amount_data(event_body, topup):
    amount = event_body.amount
    currency = event_body.currency
    if amount:
        topup.amount = amount
        topup.save()
    if currency:
        topup.currency = currency
        topup.save()

def is_live_mode(event_body, topup):
    live_mode = event_body.livemode
    if live_mode:
        topup.live_mode = live_mode
        topup.save()

def increase_balance(event_body):
    amount_received = int(event_body.amount / 100)
    user_profile_id = event_body.metadata.user_profile_id
    user_profile = Profile.objects.get(pk=user_profile_id)
    user_profile.money += amount_received
    user_profile.save()

def save_user(event_body, topup):
    user_profile_id = event_body.metadata.user_profile_id
    if user_profile_id:
        try:
            profile = Profile.objects.get(pk=user_profile_id)
            topup.user = profile.user
            topup.save()
        except Profile.DoesNotExist:
            print('error') #TODO:handle error