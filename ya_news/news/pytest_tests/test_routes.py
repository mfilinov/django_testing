from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize('name', (
        'news:home', 'users:login', 'users:logout', 'users:signup'))
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
