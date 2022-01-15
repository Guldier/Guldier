from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from payments import forms as pay_forms
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

        if event.type == 'checkout.session.completed':
            completed_checkout_session = event.data.object
            print(completed_checkout_session)
            amount_received = int(completed_checkout_session.amount_total / 100)
            user_profile_id = completed_checkout_session.metadata.user_profile_id
            profile = Profile.objects.get(pk=user_profile_id)
            profile.money += amount_received
            profile.save()
        elif event.type == 'payment_intent.payment_failed':
            return render(request, template_name='payment-failure.html')

        return HttpResponse(status=200)


class PaymentHistoryView(View):
    def get(self, request, *args, **kwargs):

        return render(request, template_name='payment-history.html')