import pytest

from django.urls import reverse

from payments.forms import TopUpForm

def test_topup_form(client, get_login_data):
    response = client.get('{}'.format(reverse('payments:top_up')))
    # user is not logged in so gets redirected to login page, from where will be taken to top up page
    assert response.status_code == 302
    assert response.url == '{}?next={}'.format(reverse('login'), reverse('payments:top_up'))
    # user is logged in so he or she can access the page
    username, password = get_login_data
    client.login(username=username, password=password)
    response = client.get('{}'.format(reverse('payments:top_up')))
    assert response.status_code == 200

def test_checkout_session(client, get_login_data):
    response = client.post('{}'.format(reverse('payments:create_checkout_session')))
    # user is not logged in so gets redirected to login page, from where will be taken to checkout session
    assert response.status_code == 302
    assert response.url == '{}?next={}'.format(reverse('login'), reverse('payments:create_checkout_session'))
    # user is logged in so he or she can access the page, but form is empty
    username, password = get_login_data
    client.login(username=username, password=password)
    response = client.post('{}'.format(reverse('payments:create_checkout_session')))
    assert response.status_code == 302
    assert response.url == reverse('payments:top_up')
    # user is logged in, but the form value is not one of accepted values  
    form = TopUpForm(data={ 'top_up_amount': 1 })
    assert form.is_valid() == False
    assert response.status_code == 302
    assert response.url == reverse('payments:top_up')
    # user is logged in and form is valid
    form = TopUpForm(data={ 'top_up_amount': 15 })
    assert form.is_valid()
    # TODO: fixture that serves all checkout session items, to receive 303?