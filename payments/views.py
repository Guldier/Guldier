from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator

from payments import forms as pay_forms
from payments import models as pay_models
from payments import schemas as pay_schemas
from urllib.parse import urljoin
from users.models import Profile
from payments.models import TopUp
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class ProductLandingPageView(LoginRequiredMixin, View):

    related_field = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = pay_forms.TopUpForm()
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'form': form,
        }
        return render(request, template_name='payments/top_up.html', context=context)


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        # get the amount that customer wants to top up his account with
        form = pay_forms.TopUpForm(request.POST)
        if form.is_valid():
            topup_value = form.cleaned_data['top_up_amount']
        else:
            return redirect('payments:top_up')
        # assign all values needed to open a checkout session with Stripe
        # get success and cancel url
        schema = 'http://'
        host = request.META['HTTP_HOST']
        hostname = host.split(':')[0]
        port = host.split(':')[1]
        success_url = urljoin(schema + hostname + ':' + port, '/payments/success')
        cancel_url = urljoin(schema + hostname + ':' + port, '/payments/cancel')
        # get line items json
        intent_value = int(topup_value) * 100
        quantity = 1
        name = 'Top up'
        currency = 'pln'
        product_data = pay_schemas.ProductData(name=name)
        price_data = pay_schemas.PriceData(currency=currency, unit_amount=intent_value, product_data=product_data)
        line_items = pay_schemas.LineItems(price_data=price_data, quantity=quantity)
        line_items_json = pay_schemas.LineItemsSchema().dump(line_items)
        # get metadatas with id of empty transaction for currently logged in user to retrieve it back in wehbhooks
        user = request.user
        topup_pk = pay_models.TopUp.payments.create(user=user).pk
        metadata = pay_schemas.Metadata(topup_pk=topup_pk)
        metadata_json = pay_schemas.MetadataSchema().dump(metadata)
        payment_intent_data = pay_schemas.PaymentIntentData(metadata=metadata)
        payment_intent_data_json = pay_schemas.PaymentIntentDataSchema().dump(payment_intent_data)
        # open checkout session with Stripe with jsons
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
        # redirect to Stripe's checkout session 
        return redirect(checkout_session.url, code=303, context={'message': 'Your account has been topped up.'})


class SuccessView(TemplateView):
    template_name = 'payments/success.html'


class CancelView(TemplateView):
    template_name = 'payments/cancel.html'


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):

    def post(self, request, *args, **kwargs):

        # endpoint_secret = "whsec_5b54e15f8aabefce01cd3d3e9f18b5dce347935384c58ea09211133145ec28e3"
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

        #get payload and type of object that came in the event
        event_body, object_type = get_event_payload_and_type(event)
        #only checkout_session, payment_intent and charge objects come back with metadata
        if getattr(event_body.metadata, 'topup_pk', None):
            topup = get_transaction_record(event_body) # find transaction's record in database
            save_id_and_status(event_body, topup, object_type) # save event's id and status
            if event.type == 'payment_intent.created':
                save_amount_data(event_body, topup) 
                is_live_mode(event_body, topup) # flags if test or live
            elif event.type == 'payment_intent.succeeded':
                increase_balance(event_body, topup) # add funds to user's account
            topup.save()
        return HttpResponse(status=200)

def get_event_payload_and_type(event):
    event_body = event.data.object
    object_type = event_body.object
    return event_body, object_type

def get_transaction_record(event_body):
    topup_pk = event_body.metadata.topup_pk
    try:
        topup = pay_models.TopUp.payments.get(pk=topup_pk)
        return topup
    except pay_models.TopUp.DoesNotExist:
        print('record with this pk does not exist') #TODO handle error
        return None

def save_id_and_status(event_body, topup, object_type):
    if object_type == 'checkout.session':
        topup.checkout_session_status = event_body.status
        topup.checkout_session_id = event_body.id
    elif object_type == 'payment_intent':
        topup.payment_intent_status = event_body.status
        topup.payment_intent_id = event_body.id
    elif object_type == 'charge':
        topup.charge_status = event_body.status
        topup.charge_id = event_body.id
    return topup

def save_email(event_body, topup):
    topup.customer_email = event_body.email
    return topup

def save_amount_data(event_body, topup):
    topup.amount = event_body.amount
    topup.currency = event_body.currency
    return topup

def is_live_mode(event_body, topup):
    topup.live_mode = event_body.livemode
    return topup

def increase_balance(event_body, topup):
    amount_received = int(event_body.amount / 100)
    user = topup.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return render(request, template_name='payments/payment_failure.html')

    profile.money = F('money') + amount_received
    profile.save()


class PaymentHistoryView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'payments/payment-history.html'
    model = TopUp
    paginate_by = 10
    ordering = '-date_created'

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user).exclude(payment_intent_status='')