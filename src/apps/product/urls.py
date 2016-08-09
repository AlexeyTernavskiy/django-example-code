# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from src.apps.product import views

urlpatterns = [
    url(r'^add/$', views.ProductCreateView.as_view(), name='add'),
    url(r'^$', views.ProductsListView.as_view(), name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.ProductDetailView.as_view(), name='detail'),
    url(r'^(?P<slug>[-\w]+)/edit/$', views.ProductUpdateView.as_view(), name='edit'),
    url(r'^(?P<slug>[-\w]+)/delete/$', views.ProductDeleteView.as_view(), name='delete'),
]
