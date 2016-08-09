# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.test import TestCase
from django.urls import reverse_lazy

from src.apps.product.factories import UserFactory, ProductFactory, CommentFactory


class ProductViewsTestCase(TestCase):
    def setUp(self):
        super(ProductViewsTestCase, self).setUp()
        self.user1 = UserFactory()
        self.user2 = UserFactory(first_name='Bart', is_staff=True)
        self.products = ProductFactory.create_batch(user=self.user1, size=13)
        self.products += ProductFactory.create_batch(user=self.user2, size=4)
        self.comments = []
        for product in self.products:
            self.comments += CommentFactory.create_batch(user=product.user,
                                                         product=product,
                                                         size=random.randrange(0, 10))
        self.client.login(username=self.user1.username, password=self.user1.password)

    def tearDown(self):
        super(ProductViewsTestCase, self).tearDown()
        UserFactory.reset_sequence()
        ProductFactory.reset_sequence()
        CommentFactory.reset_sequence()
        self.client.logout()

    def test_index(self):
        response = self.client.get(reverse_lazy('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login(self):
        response = self.client.get(reverse_lazy('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_signup(self):
        response = self.client.get(reverse_lazy('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_logout(self):
        response = self.client.get(reverse_lazy('account_logout'))
        self.assertRedirects(response, reverse_lazy('index'))

    def test_product_list(self):
        response = self.client.get(reverse_lazy('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 5)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: product_name_16>',
                                  '<ProductModel: product_name_15>',
                                  '<ProductModel: product_name_14>',
                                  '<ProductModel: product_name_13>',
                                  '<ProductModel: product_name_12>'])

    def test_product_list_pagination(self):
        response = self.client.get(reverse_lazy('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 5)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: product_name_16>',
                                  '<ProductModel: product_name_15>',
                                  '<ProductModel: product_name_14>',
                                  '<ProductModel: product_name_13>',
                                  '<ProductModel: product_name_12>'])
        response = self.client.get(reverse_lazy('products:list') + '?page=4')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 2)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: product_name_1>',
                                  '<ProductModel: product_name_0>'])
        response = self.client.get(reverse_lazy('products:list') + '?page=5')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
