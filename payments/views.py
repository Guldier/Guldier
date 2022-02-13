
import stripe

from django import views
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator

from payments import forms as pay_forms
from payments import models as pay_models
from payments import schemas as pay_schemas
from urllib.parse import urljoin
from users.models import Profile
from payments.models import Address, TopUp, Invoice

stripe.api_key = settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class ProductLandingPageView(LoginRequiredMixin, View):
    related_field = 'redirect_to'

    def get(self, request, *args, **kwargs):
        try:
            last_address = Address.objects.all().filter(user=request.user).latest('date_created')
        except Address.DoesNotExist:
            last_address = None 
        form = pay_forms.AmountAddressForm(instance=last_address)
        context = {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'form': form,
        }
        return render(request, template_name='payments/top_up.html', context=context)


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        user = request.user
        form = pay_forms.AmountAddressForm(request.POST)
        if form.is_valid():
        # get the amount that customer wants to top up his account with
            topup_value = form.cleaned_data['top_up_amount']
        # get the address for invoice
            address = Address.objects.create(
                user=user, 
                name = form.cleaned_data['name'],
                surname = form.cleaned_data['surname'],
                street_and_number = form.cleaned_data['street_and_number'],
                city = form.cleaned_data['city'],
                country = form.cleaned_data['country'],
                postal_code = form.cleaned_data['postal_code'],
            )
        else:
            context = {
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                'form': form,
            }
            return render(request, template_name='payments/top_up.html', context=context)
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
        topup_pk = pay_models.TopUp.payments.create(user=user).pk
        metadata = pay_schemas.Metadata(topup_pk=topup_pk, address_pk=address.pk)
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
            topup = get_transaction_record(event_body)
            # find transaction's record in database
            save_id_and_status(event_body, topup, object_type)  # save event's id and status
            if event.type == 'payment_intent.created':
                save_amount_data(event_body, topup)
                is_live_mode(event_body, topup)  # flags if test or live
            elif event.type == 'payment_intent.succeeded':
                increase_balance(request, event_body, topup) # add funds to user's account
                topup.save()
                invoice = topup.create_invoice(event_body)
                if invoice:
                    invoice.send_email_with_invoice(request) # send invoice to currently logged user's (! )e-mail

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

def increase_balance(request, event_body, topup):
    amount_received = int(event_body.amount / 100)
    user = topup.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return render(request, template_name='payments/payment_failure.html')

    profile.money = F('money') + amount_received
    profile.save()


class GetInvoiceView(LoginRequiredMixin, views.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            invoice_pk = self.kwargs['invoice_pk']
            invoice = get_object_or_404(Invoice, pk=invoice_pk)
            response = HttpResponse(content=b'',headers={
                'Content-Type': 'application/pdf',
                'Content-Disposition': 'attachment; filename={}'.format(invoice.name),
            })
            invoice.write_invoice_to_pdf(request, response)
            return response
        else:
            return HttpResponse(status=403, content="Sorry, you're not authorised to see this content.")


class PaymentHistoryView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'payments/payment-history.html'
    model = TopUp
    paginate_by = 10
    ordering = '-date_created'

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(user=user).exclude(payment_intent_status='')
