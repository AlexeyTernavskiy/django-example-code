# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView, DetailView

from src.apps.product.models import ProductModel


class ProductsListView(ListView):
    model = ProductModel
    template_name = 'product/products.html'
    context_object_name = 'products'
    paginate_by = 5


class ProductDetailView(DetailView):
    model = ProductModel
    template_name = 'product/product.html'
    context_object_name = 'product'
