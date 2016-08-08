# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.account import views
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^signup/$', views.signup, name='account_signup'),
    url(r'^login/$', views.login, name='account_login'),
    url(r'^logout/$', views.logout, name='account_logout'),
    url(r'^products/', include('src.apps.product.urls', namespace='products'))
]
