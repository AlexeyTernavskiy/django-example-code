# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import ListView, DetailView
from pure_pagination import PaginationMixin

from src.apps.product.forms import FilterForm, ProductForm
from src.apps.product.models import ProductModel


class ProductsListView(PaginationMixin, ListView):
    model = ProductModel
    template_name = 'product/products.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset().select_related('user').annotate(
            like_total=Count('like'))
        if 'filter' in self.request.GET:
            select = self.request.GET['filter']
            if select != '' and select in filter(None, FilterForm.FILTER_CHOICE._db_values):
                return queryset.order_by(select)
        else:
            return queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsListView, self).get_context_data(**kwargs)
        context['filters'] = FilterForm(self.request.GET)
        return context


class ProductDetailView(DetailView):
    model = ProductModel
    queryset = ProductModel.objects.select_related('user').annotate(like_total=Count('like'))
    template_name = 'product/product.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    form_class = ProductForm
    template_name = 'product/form.html'

    def get_success_url(self, **kwargs):
        return reverse('products:detail', kwargs={
            'slug': kwargs.get('slug')
        })

    def form_valid(self, form):
        form = form.save(commit=False)
        form.user = self.request.user
        form.name = form.name.capitalize()
        form.description = form.description.capitalize()
        form.slug = re.sub("^\s+|\n|\r|\s+$", '', form.name.lower()).replace(' ', '-')
        form.save()
        return redirect(self.get_success_url(slug=form.slug))
