# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

import factory
from django.contrib.auth import get_user_model

from src.apps.product.models import ProductModel, CommentModel

User = get_user_model()
USER_PASSWORD = 'qwerty'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = 'Homer'
    last_name = 'Simpson'
    username = factory.LazyAttribute(lambda n: '{0}{1}'.format(n.first_name,
                                                               n.last_name).lower())
    email = factory.LazyAttribute(lambda n: '{0}.{1}@example.com'.format(n.first_name,
                                                                         n.last_name).lower())
    password = factory.PostGenerationMethodCall('set_password', USER_PASSWORD)
    is_superuser = False
    is_staff = False
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductModel

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'product_name_{}'.format(n))
    slug = factory.Sequence(lambda n: 'product_slug_{}'.format(n))
    description = factory.Sequence(lambda n: 'product_description_{}'.format(n))
    price = factory.LazyAttribute(lambda n: random.randrange(0, 1000, 4))


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentModel

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    comment = factory.LazyAttribute(lambda n: 'comment for {}'.format(n.product))


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentModel

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
