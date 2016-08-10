# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
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

from src.apps.product.forms import FilterForm, ProductForm, CommentForm
from src.apps.product.models import ProductModel, LikeModel, CommentModel


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

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['comments'] = CommentModel.objects.select_related('user', 'product').filter(
            product=self.object,
            created__gte=datetime.datetime.now() - datetime.timedelta(days=1)
        ).order_by('-created')
        context['form'] = CommentForm()
        return context


class DispatchMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if 'slug' in kwargs:
                product = get_object_or_404(ProductModel, slug=kwargs.get('slug'))
                if product.user != request.user:
                    messages.add_message(request, messages.WARNING, 'You can not do this action')
                    return redirect(reverse('products:detail', args=(kwargs.get('slug'),)))
        return super(DispatchMixin, self).dispatch(request, *args, **kwargs)


class ProductCreateUpdateMixin(DispatchMixin):
    form_class = ProductForm
    template_name = 'product/form.html'

    def get_success_url(self, **kwargs):
        return reverse('products:detail', kwargs={
            'slug': kwargs.get('slug')
        })

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        if 'name' in request.POST:
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


class ProductDeleteView(DispatchMixin, DeleteView):
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
                status = 200
            except LikeModel.DoesNotExist:
                LikeModel.objects.create(user=request.user, product=product)
                msg = 'Like added'
                status = 201
            return JsonResponse({'message': msg, 'like_count': product.like.count()}, status=status)


class CommentView(CreateView):
    model = CommentModel
    form_class = CommentForm
    context_object_name = 'comment'

    comment_html = '''<div class="media" data-id={comment_id}>
                            <a class="media-left" href="#">
                                <img class="media-object" src="http://placehold.it/50x50" alt="User Photo">
                            </a>
                        <div class="media-body">
                            <h4 class="media-heading">{author}</h4>
                            <p>{comment}</p>
                        </div>
                        <div class="media-footer">
                            <p>{created}</p>
                        </div>
                    </div>'''

    def get_success_url(self, **kwargs):
        return reverse('products:detail', kwargs={
            'slug': kwargs.get('slug')
        })

    def get(self, request, *args, **kwargs):
        return redirect(reverse('products:detail', kwargs={'slug': kwargs['slug']}))

    def post(self, request, *args, **kwargs):
        if 'last' in self.request.path and 'id' in self.request.POST:
            response_data = dict()
            html = ''
            response_data['disabled'] = False
            if self.request.POST['id'] == '0':
                comments = CommentModel.objects.prefetch_related('user', 'product').filter(
                    product_id=self.kwargs['slug']).order_by('-created')[:5]
                if comments.count() < 5:
                    response_data['disabled'] = True
            else:
                date = CommentModel.objects.get(id=int(self.request.POST['id'])).created
                comments = CommentModel.objects.prefetch_related('user', 'product').filter(
                    product_id=self.kwargs['slug'], created__lt=date).order_by('-created')[:5]
                if comments.count() < 5:
                    response_data['disabled'] = True
            for comment in comments:
                author = 'Anonymous'
                created = comment.created.strftime("%B %d, %Y, %-I:%M %p")
                if comment.user is not None:
                    author = comment.user.username
                html += ''.join(self.comment_html.format(comment_id=comment.id,
                                                         author=author,
                                                         comment=comment.comment,
                                                         created=created))
            response_data['html'] = html
            return JsonResponse(response_data, status=200)
        return super(CommentView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        response_data = dict()
        if self.request.is_ajax():
            form = form.save(commit=False)
            product = ProductModel.objects.get(slug=self.kwargs.get('slug'))
            if self.request.user.is_anonymous():
                form.user = None
                author = 'Anonymous'
            else:
                form.user = self.request.user
                author = form.user.username
            form.product = product
            form.save()
            comment_id = CommentModel.objects.all().order_by('created').last().id
            comment = form.comment
            created = form.created.strftime('%B %d, %Y, %I:%M %p')
            response_data['message'] = 'Your comment has successfully added'
            response_data['html'] = self.comment_html.format(comment_id=comment_id,
                                                             author=author,
                                                             comment=comment,
                                                             created=created)
        return JsonResponse(response_data, status=200)

    def form_invalid(self, form):
        if self.request.is_ajax():
            message = form.errors['comment'][0]
            return JsonResponse({'message': message}, status=400)
