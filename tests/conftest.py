import pytest

from payments.models import TopUp

from users.models import Profile


@pytest.fixture
def get_topup(user=None, amount=None, currency=None):
    test_topup = TopUp.payments.create(user=user, amount=amount, currency=currency)
    return test_topup

@pytest.fixture
def get_login_data(django_user_model):
    username = 'homer'
    password = 'homie'
    user = django_user_model.objects.create(username=username)
    user.set_password(password)
    user.save()
    return username, password