# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from src.apps.product.factories import UserFactory, ProductFactory, CommentFactory, LikeFactory, USER_PASSWORD
from src.apps.product.models import ProductModel, CommentModel


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
                                                         size=3)
        self.client.force_login(user=self.user1, backend=settings.AUTHENTICATION_BACKENDS[0])

    def tearDown(self):
        super(ProductViewsTestCase, self).tearDown()
        UserFactory.reset_sequence()
        ProductFactory.reset_sequence()
        CommentFactory.reset_sequence()
        self.client.logout()

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        response = self.client.get(reverse('account_login'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue(response.context['user'].is_authenticated)

        self.client.logout()

        response = self.client.get(reverse('account_login'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        response = self.client.post(reverse('account_login'), follow=True, data={
            'login': self.user1.username,
            'password': USER_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_form(self):
        self.client.logout()

        response = self.client.get(reverse('account_login'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        response = self.client.post(reverse('account_login'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertFormError(response, 'form', 'login', 'This field is required.')
        self.assertFormError(response, 'form', 'password', 'This field is required.')

        response = self.client.post(reverse('account_login'), data=dict(login='qwerty', password='qwerty'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertFormError(response, 'form', field=None,
                             errors='The username and/or password you specified are not correct.')

        response = self.client.post(reverse('account_login'), follow=True, data={
            'login': self.user1.username,
            'password': USER_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'index.html')
        msg = next(iter(response.context['messages']))
        self.assertEqual(msg.message, 'Successfully signed in as {}.'.format(self.user1.username))

    def test_signup(self):
        username = 'newuser'
        password = 'qwe123qwe123'

        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        response = self.client.get(reverse('account_signup'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTrue(response.context['user'].is_authenticated)

        self.client.logout()

        response = self.client.get(reverse('account_signup'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=username)

        response = self.client.post(reverse('account_signup'), follow=True, data={
            'username': username,
            'password1': password,
            'password2': password
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], User.objects.get(username=username))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'index.html')

    def test_signup_form(self):
        username = 'newuser'
        password = 'qwe123qwe123'

        self.client.logout()

        response = self.client.get(reverse('account_signup'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

        response = self.client.post(reverse('account_signup'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'password1', 'This field is required.')
        self.assertFormError(response, 'form', 'password2', 'This field is required.')

        response = self.client.post(reverse('account_signup'), data=dict(username='qwe'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertEqual(re.sub(r'\s+', ' ', response.context['form'].errors['username'][0]),
                         'Nickname length should be more than 3 characters')
        self.assertFormError(response, 'form', 'password1', 'This field is required.')
        self.assertFormError(response, 'form', 'password2', 'This field is required.')

        response = self.client.post(reverse('account_signup'), data=dict(username='qwerty',
                                                                         password1='qwe',
                                                                         password2='qwe'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertFormError(response, 'form', 'password1', 'Password must be a minimum of 6 characters.')

        response = self.client.post(reverse('account_signup'), data=dict(username='qwerty',
                                                                         password1='qwqwqwqw',
                                                                         password2='qwqwqwqwqw'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertFormError(response, 'form', field=None, errors='You must type the same password each time.')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=username)
        self.assertEqual(User.objects.all().count(), 2)
        response = self.client.post(reverse('account_signup'), follow=True, data={
            'username': username,
            'password1': password,
            'password2': password
        })
        self.assertEqual(User.objects.all().count(), 3)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'index.html')
        m = next(iter(response.context['messages']))
        self.assertEqual(m.message, 'Successfully signed in as {}.'.format(username))

    def test_logout(self):
        response = self.client.get(reverse('account_logout'))
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/logout.html')

        response = self.client.post(reverse('account_logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        m = next(iter(response.context['messages']))
        self.assertEqual(m.message, 'You have signed out.')

        response = self.client.get(reverse('account_logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(response.context['user'].is_authenticated)

        response = self.client.post(reverse('account_logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_product_list(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 5)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: Product_name_16>',
                                  '<ProductModel: Product_name_15>',
                                  '<ProductModel: Product_name_14>',
                                  '<ProductModel: Product_name_13>',
                                  '<ProductModel: Product_name_12>'])

    def test_product_list_pagination(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 5)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: Product_name_16>',
                                  '<ProductModel: Product_name_15>',
                                  '<ProductModel: Product_name_14>',
                                  '<ProductModel: Product_name_13>',
                                  '<ProductModel: Product_name_12>'])

        response = self.client.get(reverse('products:list') + '?page=4')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        self.assertEqual(response.context['products'].count(), 2)
        self.assertQuerysetEqual(response.context['products'],
                                 ['<ProductModel: Product_name_1>',
                                  '<ProductModel: Product_name_0>'])

        response = self.client.get(reverse('products:list') + '?page=5')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_product_list_filtration(self):
        # Default queryset ordered by last created
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context['products'][0].created, response.context['products'][1].created)

        # Queryset filtering by created
        response = self.client.get(reverse('products:list') + '?filter=created')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(response.context['products'][0].created, response.context['products'][1].created)

        # Queryset filtering by -created
        response = self.client.get(reverse('products:list') + '?filter=-created')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context['products'][0].created, response.context['products'][1].created)

        # Queryset filtering by price
        response = self.client.get(reverse('products:list') + '?filter=price')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(response.context['products'][0].price, response.context['products'][1].price)

        # Queryset filtering by -price
        response = self.client.get(reverse('products:list') + '?filter=-price')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.context['products'][0].price, response.context['products'][1].price)

        # Create likes for product
        LikeFactory(user=self.user1, product=self.products[10])
        LikeFactory(user=self.user2, product=self.products[11])

        # Queryset filtering by like
        response = self.client.get(reverse('products:list') + '?filter=like')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(response.context['products'], [self.products[10], self.products[11]])

        # Queryset filtering by -like
        response = self.client.get(reverse('products:list') + '?filter=-like')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'][0], self.products[11])
        self.assertEqual(response.context['products'][0].slug, self.products[11].slug)
        self.assertEqual(response.context['products'][1], self.products[10])
        self.assertEqual(response.context['products'][1].slug, self.products[10].slug)

    def test_product_list_pagination_with_filtration(self):
        response = self.client.get(reverse('products:list') + '?page=1&filter=-price')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'].count(), 5)

        self.assertGreaterEqual(response.context['products'][0].price, response.context['products'][1].price)
        response = self.client.get(reverse('products:list') + '?page=4&filter=-price')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'].count(), 2)

        self.assertGreaterEqual(response.context['products'][0].price, response.context['products'][1].price)
        response = self.client.get(reverse('products:list') + '?page=5&filter=-price')
        self.assertEqual(response.status_code, 404)

    def test_product_create_unauth(self):
        self.client.logout()

        response = self.client.get(reverse('products:add'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login') + '?next=/products/add/')

        response = self.client.get(reverse('products:add'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        response = self.client.post(reverse('account_login'), follow=True, data={
            'login': self.user1.username,
            'password': USER_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

        response = self.client.get(reverse('products:add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertContains(response, 'Add new Product')

    def test_product_create_auth(self):
        product = {
            'user': self.user1,
            'name': 'New product',
            'slug': 'new-product',
            'description': 'Description for New Product',
            'price': 123
        }

        response = self.client.get(reverse('products:add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertContains(response, 'Add new Product')
        self.assertEqual(ProductModel.objects.all().count(), 17)
        with self.assertRaises(ProductModel.DoesNotExist):
            ProductModel.objects.get(slug=product['slug'])

        response = self.client.post(reverse('products:add'), follow=True, data=product)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(ProductModel.objects.all().count(), 18)
        self.assertEqual(ProductModel.objects.get(slug=product['slug']).user, product['user'])
        m = next(iter(response.context['messages']))
        self.assertEqual(m.message, 'Product {} successfully added'.format(product['name']))

    def test_product_create_form(self):
        response = self.client.post(reverse('products:add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        self.assertFormError(response, 'form', 'description', 'This field is required.')
        self.assertFormError(response, 'form', 'price', 'This field is required.')

        response = self.client.post(reverse('products:add'), data=dict(
            name='prod',
            description='asdsa',
            price=0
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertFormError(response, 'form', 'price', 'Ensure this value is greater than or equal to 0.01.')
        data = dict(
            name='New product',
            description='asdsa',
            price=1
        )
        self.assertEqual(ProductModel.objects.all().count(), 17)
        with self.assertRaises(ProductModel.DoesNotExist):
            ProductModel.objects.get(slug=data['name'])

        response = self.client.post(reverse('products:add'), follow=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(ProductModel.objects.all().count(), 18)
        self.assertEqual(ProductModel.objects.get(name=data['name']).user, response.context['user'])
        m = next(iter(response.context['messages']))
        self.assertEqual(m.message, 'Product {} successfully added'.format(data['name']))

        response = self.client.post(reverse('products:add'), follow=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertFormError(response, 'form', 'name', 'Product with this Name of product already exists.')
        self.assertEqual(ProductModel.objects.all().count(), 18)

    def test_product_update_unauth(self):
        product = self.products[0]
        url = reverse('products:edit', args=(product.slug,))
        self.client.logout()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login') + '?next=/products/product_slug_0/edit/')

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        response = self.client.post(reverse('account_login'), follow=True, data={
            'login': self.user1.username,
            'password': USER_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/form.html')
        self.assertContains(response, 'Edit {}'.format(product.name))

    def test_product_update_auth(self):
        pass

    def test_product_update_form(self):
        pass

    def test_product_delete_unauth(self):
        product = self.products[0]
        url = reverse('products:delete', args=(product.slug,))
        self.client.logout()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_login') + '?next=/products/product_slug_0/delete/')

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

        response = self.client.post(reverse('account_login'), follow=True, data={
            'login': self.user1.username,
            'password': USER_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/delete.html')
        self.assertContains(response, 'Delete product {}'.format(product.name))

    def test_product_delete_auth(self):
        product = self.products[0]
        url = reverse('products:delete', args=(product.slug,))

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/delete.html')
        self.assertEqual(ProductModel.objects.all().count(), 17)

        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/products.html')
        msg = next(iter(response.context['messages']))
        self.assertEqual(msg.message, 'Product {} successfully deleted'.format(product.name))
        self.assertEqual(ProductModel.objects.all().count(), 16)
        with self.assertRaises(ProductModel.DoesNotExist):
            ProductModel.objects.get(slug=product.slug)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_like_unauth(self):
        self.client.logout()

        product = self.products[0]
        url = reverse('products:detail', args=(product.slug,))

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertIsInstance(response.context['product'], ProductModel)
        self.assertEqual(response.context['product'], product)

        response = self.client.get(url + 'like/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')

        response = self.client.post(url + 'like/', follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['message'], 'To perform this action, you must be logged.')

    def test_like_auth(self):
        product = self.products[0]
        url = reverse('products:detail', args=(product.slug,))

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(response.context['product'], product)

        response = self.client.get(url + 'like/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(product.like.count(), 0)

        response = self.client.post(url + 'like/', follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['message'], 'Like added')
        self.assertEqual(data['like_count'], 1)
        self.assertEqual(product.like.count(), data['like_count'])

        response = self.client.post(url + 'like/', follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['message'], 'Like deleted')
        self.assertEqual(data['like_count'], 0)
        self.assertEqual(product.like.count(), data['like_count'])

    def test_comment(self):
        product = self.products[0]
        url = reverse('products:detail', args=(product.slug,))

        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(response.context['product'], product)

        response = self.client.get(url + 'comment/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(CommentModel.objects.filter(product=product).count(), 3)

        response = self.client.post(url + 'comment/', follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data=dict(comment='New Comment'))
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['message'], 'Your comment has successfully added')
        self.assertEqual(CommentModel.objects.filter(product=product).count(), 4)

        response = self.client.post(url + 'comment/', follow=True, data=dict(comment='New Comment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product.html')
        self.assertEqual(CommentModel.objects.filter(product=product).count(), 5)
        msg = next(iter(response.context['messages']))
        self.assertEqual(msg.message, 'Comment successfully added')

        response = self.client.post(url + 'comment/', follow=True)
        self.assertEqual(response.status_code, 200)
        msg = next(iter(response.context['messages']))
        self.assertEqual(msg.message, 'The body of the comment should not be empty')
        self.assertEqual(CommentModel.objects.filter(product=product).count(), 5)
