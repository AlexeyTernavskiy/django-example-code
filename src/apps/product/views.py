# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView, DetailView
from django.views.generic import UpdateView
from pure_pagination import PaginationMixin

from src.apps.product.forms import FilterForm, ProductForm
from src.apps.product.models import ProductModel, LikeModel


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


class ProductCreateUpdateMixin(LoginRequiredMixin):
    form_class = ProductForm
    template_name = 'product/form.html'

    def get_success_url(self, **kwargs):
        return reverse('products:detail', kwargs={
            'slug': kwargs.get('slug')
        })

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST['name'] = request.POST['name'].capitalize()
        return super(ProductCreateUpdateMixin, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form = form.save(commit=False)
        form.user = self.request.user
        form.name = form.name
        form.description = form.description.capitalize()
        form.slug = re.sub("^\s+|\n|\r|\s+$", '', form.name.lower()).replace(' ', '-')
        form.save()

        return redirect(self.get_success_url(slug=form.slug))


class ProductCreateView(ProductCreateUpdateMixin, CreateView):
    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO,
                             'Product {} successfully added'.format(self.request.POST['name']))
        return super(ProductCreateView, self).get_success_url(**kwargs)


class ProductUpdateView(ProductCreateUpdateMixin, UpdateView):
    model = ProductModel
    context_object_name = 'product'

    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO,
                             'Product {} successfully changed'.format(self.object.name))
        return super(ProductUpdateView, self).get_success_url(**kwargs)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductModel
    context_object_name = 'product'
    template_name = 'product/delete.html'
    success_url = '/products/'

    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.INFO,
                             'Product {} successfully deleted'.format(self.object.name))
        return super(ProductDeleteView, self).get_success_url()


class LikeView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            if request.is_ajax():
                return JsonResponse({'message': 'To perform this action, you must be logged.'}, status=403)
            else:
                return self.get(request, *args, **kwargs)
        return super(LikeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect(reverse('products:detail', kwargs={'slug': kwargs['slug']}))

    def post(self, request, **kwargs):
        if request.is_ajax():
            product = get_object_or_404(ProductModel.objects, slug=kwargs.get('slug'))
            try:
                LikeModel.objects.get(user=request.user, product=product).delete()
                msg = 'Like deleted'
            except LikeModel.DoesNotExist:
                LikeModel.objects.create(user=request.user, product=product)
                msg = 'Like added'
            return JsonResponse({'message': msg, 'like_count': product.like.count()}, status=200)
