# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Count
from django.views.generic import ListView, DetailView
from pure_pagination import PaginationMixin

from src.apps.product.forms import FilterForm
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
    template_name = 'product/product.html'
    context_object_name = 'product'
