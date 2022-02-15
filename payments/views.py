import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView
from users.models import Profile

from .forms import TopUpForm
from .models import TopUp
from .schemas import (
    LineItems,
    LineItemsSchema,
    Metadata,
    MetadataSchema,
    PaymentIntentData,
    PaymentIntentDataSchema,
    PriceData,
    ProductData
)

stripe.api_key = settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class ProductLandingPageView(LoginRequiredMixin, View):
    related_field = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = TopUpForm()
        context = {
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            'form': form,
        }
        return render(request, template_name='top_up.html', context=context)


class CreateCheckoutSessionView(FormView):

    form_class = TopUpForm

    def form_valid(self, form):
        topup_value = form.cleaned_data['amount']
        success_url = self.request.build_absolute_uri(reverse('payments:success'))
        cancel_url = self.request.build_absolute_uri(reverse('payments:cancel'))
        intent_value = int(topup_value) * 100
        topup_data = settings.TOPUP_DATA
        product_data = ProductData(name=topup_data['name'])
        price_data = PriceData(currency=topup_data['currency'], unit_amount=intent_value, product_data=product_data)
        line_items = LineItems(price_data=price_data, quantity=topup_data['quantity'])
        line_items_json = LineItemsSchema().dump(line_items)
        # get metadatas with id of empty transaction for currently logged in user to retrieve it back in wehbhooks
        user = self.request.user
        topup_pk = TopUp.payments.create(user=user).pk
        metadata = Metadata(topup_pk=topup_pk)
        metadata_json = MetadataSchema().dump(metadata)
        payment_intent_data = PaymentIntentData(metadata=metadata)
        payment_intent_data_json = PaymentIntentDataSchema().dump(payment_intent_data)
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
        return redirect(checkout_session.url, code=303)

    def form_invalid(self, form):
        return redirect('payments:top_up')


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

        # get payload and type of object that came in the event
        event_body, object_type = get_event_payload_and_type(event)
        # only checkout_session, payment_intent and charge objects come back with metadata
        if getattr(event_body.metadata, 'topup_pk', None):
            topup = get_transaction_record(event_body)  # find transaction's record in database
            save_id_and_status(event_body, topup, object_type)  # save event's id and status
            if event.type == 'payment_intent.created':
                save_amount_data(event_body, topup)
                is_live_mode(event_body, topup)  # flags if test or live
            elif event.type == 'payment_intent.succeeded':
                increase_balance(event_body, topup)  # add funds to user's account
            topup.save()
        return HttpResponse(status=200)


def get_event_payload_and_type(event):
    event_body = event.data.object
    object_type = event_body.object
    return event_body, object_type


def get_transaction_record(event_body):
    topup_pk = event_body.metadata.topup_pk
    try:
        topup = TopUp.payments.get(pk=topup_pk)
        return topup
    except TopUp.DoesNotExist:
        return HttpResponse(status=404)


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
    except ObjectDoesNotExist:
        return render(request, template_name='payment_failure.html')

    profile.money = F('money') + amount_received
    profile.save()


@method_decorator(login_required, name='dispatch')
class PaymentHistoryView(View):
    def get(self, request):
        user_payments = TopUp.payments.filter(user=request.user).filter(~Q(payment_intent_status='')).order_by(
            '-date_created')
        for payment in user_payments:
            payment.amount = payment.amount / 100
        paginator = Paginator(user_payments, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, template_name='payment-history.html',
                      context={'page_obj': page_obj})
