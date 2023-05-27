from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='News Title',
        text='News Text',
    )
    return news


@pytest.fixture
def pk_from_news(news):
    return news.pk,


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Comment text'
    )
    return comment


@pytest.fixture
def pk_from_comment(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def make_bulk_of_news():
    News.objects.bulk_create(
        News(title=f'News number {index}',
             text='News text',
             date=datetime.today() - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def make_bulk_of_comments(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment text {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
