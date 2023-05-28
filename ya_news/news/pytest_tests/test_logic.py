from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, pk_from_news, form_data):
    url = reverse('news:detail', args=pk_from_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments, (
        f'Создано {comments_count} комментариев,'
        f' ожидалось {expected_comments}')


def test_user_can_create_comment(
        admin_user, admin_client, news, form_data):
    url = reverse('news:detail', args=[news.pk])
    response = admin_client.post(url, data=form_data)
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments, (
        f'Создано {comments_count} комментариев,'
        f' ожидалось {expected_comments}')
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, pk_from_news):
    bad_words_data = {'text': f'Какой-то text, {choice(BAD_WORDS)}, еще text'}
    url = reverse('news:detail', args=pk_from_news)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments


def test_author_can_edit_comment(
        author_client, pk_from_news, comment, form_data):
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=pk_from_news) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text'], (
        f'Комментарий "{comment.text}" не был обновлен ,'
        f' ожидалось {form_data["text"]}')


def test_author_can_delete_comment(
        author_client, pk_from_news, pk_from_comment):
    url = reverse('news:delete', args=pk_from_comment)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=pk_from_news) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments, (
        f'Создано {comments_count} комментариев,'
        f' ожидалось {expected_comments}')


def test_other_user_cant_edit_comment(
        admin_client, pk_from_news, comment, form_data):
    url = reverse('news:edit', args=[comment.pk])
    old_comment = comment.text
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment, (
        f'Комментарий "{comment.text}" был обновлен,'
        f' ожидался {old_comment}')


def test_other_user_cant_delete_comment(
        admin_client, pk_from_news, pk_from_comment):
    url = reverse('news:delete', args=pk_from_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments, (
        f'Создано {comments_count} комментариев,'
        f' ожидалось {expected_comments}')
