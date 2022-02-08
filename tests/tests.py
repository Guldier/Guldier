import pytest

from django.urls import reverse

def test_an_admin_view(client, admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200
    response = client.get('/admin/')
    assert response.status_code == 302
    assert reverse('login') in response.url