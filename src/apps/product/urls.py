# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from src.apps.product import views

urlpatterns = [
    url(r'^add/$', views.ProductCreateView.as_view(), name='add'),
    url(r'^$', views.ProductsListView.as_view(), name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.ProductDetailView.as_view(), name='detail'),
]
